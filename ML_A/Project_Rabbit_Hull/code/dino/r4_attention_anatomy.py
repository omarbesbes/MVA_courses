"""R4 — attention anatomy and residual decomposition (100 images; trained model and random-weights twin).

Hooks on every block give x_in[l], attn[l] = ls1(attn(norm1(x))), mlp[l] = ls2(mlp(norm2(.))), x_out[l].

 (i)   residual identity  x_12 = x_0 + sum_l attn_l + sum_l mlp_l            (max abs error, float64 sum)
 (ii)  decomposition of the final pre-norm patch tokens: f_T = <T, x_12> / ||x_12||^2 for each term T
       (embedding, 12 attention updates, 12 MLP updates; they sum to 1), averaged over tokens; the same after
       subtracting from every term its mean over the 256 patch tokens of the image ("centred")
 (iii) last block: the attention update recomputed as  sum_h W_O^(h) alpha_h V_h + b_O  (then LayerScale)
       against the module's own output (max abs difference)
 (iv)  per block and head, over patch-token queries: entropy of alpha (nats), exp(entropy), top-1 mass,
       mass on the 5 special tokens, mass on the query's own position
 (v)   last block: numerical rank of the 261 x 64 key matrix of each head (and of [K, 1])
 extras (not in the brief, used for the hypotheses B1 and B4):
 (vi)  per block: how many heads contribute to the attention update of a token (norms of the 12 per-head
       contributions W_O^(h) alpha_h V_h after LayerScale: participation ratio, share of heads above 10% / 50%
       of the largest one)
 (vii) per block and head: share of the variance of the value vectors v_j (patch tokens) explained by the
       token position alone, i.e. the image-independent part of the "vertices" of Prop. 1
"""
import os
import sys
import time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import dino, rnd, save_json, summ  # noqa: E402

N_PER_CLASS = 10
BS = 10
NS = dino.N_SPECIAL


def run(model, items, name):
    L, H = 12, 12
    W_all = [blk.attn.proj.weight.detach() for blk in model.blocks]
    n_tok = 0
    terms = ["emb"] + [f"attn{l + 1}" for l in range(L)] + [f"mlp{l + 1}" for l in range(L)] + ["emb_patch", "emb_pos"]
    f_ratio = {v: np.zeros(len(terms)) for v in ("raw", "centred")}          # sum over tokens of per-token ratios
    f_num = {v: np.zeros(len(terms)) for v in ("raw", "centred")}            # pooled numerators
    f_den = {"raw": 0.0, "centred": 0.0}
    term_norm = np.zeros(len(terms))
    x12_norm, x12c_norm = [], []
    resid_err, resid_scale = 0.0, 0.0
    att = {k: np.zeros((L, H)) for k in ("entropy", "exp_entropy", "top1", "special", "self")}
    heads = {k: np.zeros(L) for k in ("participation", "frac_above_10pct_of_max", "frac_above_50pct_of_max",
                                      "min_share", "max_share")}
    head_share_sum = np.zeros((L, H))
    v_sum = torch.zeros(L, H, dino.N_PATCH, 64, dtype=torch.float64)
    v_sq = torch.zeros(L, H, dtype=torch.float64)
    recompute_err, recompute_scale = 0.0, 0.0
    key_rank, key_rank_aug, key_rank_1pct, key_sv = [], [], [], []
    n_img = 0
    for b in range(0, len(items), BS):
        x = dino.load_batch(items[b:b + BS])
        B = x.shape[0]
        with torch.no_grad(), dino.Recorder(model, attn_inputs=True) as rec:
            out = model.forward_features(x)
            x12 = out["x_prenorm"]
            # ---- (i)
            s = rec.x_in[0].double()
            for l in range(L):
                s = s + rec.attn[l].double() + rec.mlp[l].double()
            resid_err = max(resid_err, float((s - x12.double()).abs().max()))
            resid_scale = max(resid_scale, float(x12.abs().max()))
            # ---- (ii)
            emb_patch = model.patch_embed(x).double()                         # B x 256 x 768
            emb = rec.x_in[0][:, NS:].double()
            T = [emb] + [rec.attn[l][:, NS:].double() for l in range(L)] + [rec.mlp[l][:, NS:].double() for l in range(L)]
            T += [emb_patch, emb - emb_patch]
            xp = x12[:, NS:].double()
            for variant in ("raw", "centred"):
                if variant == "centred":
                    T = [t - t.mean(1, keepdim=True) for t in T]
                    xp = xp - xp.mean(1, keepdim=True)
                den = (xp ** 2).sum(-1)                                       # B x 256
                for i, t in enumerate(T):
                    num = (t * xp).sum(-1)
                    f_ratio[variant][i] += float((num / den).sum())
                    f_num[variant][i] += float(num.sum())
                    if variant == "raw":
                        term_norm[i] += float(t.norm(dim=-1).sum())
                f_den[variant] += float(den.sum())
                (x12_norm if variant == "raw" else x12c_norm).append(den.sqrt().flatten().numpy())
            n_tok += B * dino.N_PATCH
            # ---- (iii)-(vii)
            for l, blk in enumerate(model.blocks):
                alpha, v, q, k = dino.attention_parts(blk, rec.attn_in[l])    # B x H x N x N, B x H x N x 64
                a = alpha[:, :, NS:, :]
                ent = -(a * torch.log(a.clamp_min(1e-30))).sum(-1)            # B x H x 256
                att["entropy"][l] += ent.sum((0, 2)).numpy()
                att["exp_entropy"][l] += ent.exp().sum((0, 2)).numpy()
                att["top1"][l] += a.max(-1).values.sum((0, 2)).numpy()
                att["special"][l] += a[..., :NS].sum(-1).sum((0, 2)).numpy()
                att["self"][l] += torch.diagonal(alpha[:, :, NS:, NS:], dim1=-2, dim2=-1).sum((0, 2)).numpy()
                z = alpha @ v                                                 # B x H x N x 64: convex combinations
                gam = blk.ls1.gamma.detach() if hasattr(blk.ls1, "gamma") else torch.ones(dino.DIM)
                contrib = torch.einsum("bhnk,dhk->bhnd", z, W_all[l].view(dino.DIM, H, 64)) * gam
                nrm = contrib[:, :, NS:].norm(dim=-1).double()                # B x H x 256
                share = nrm / nrm.sum(1, keepdim=True)
                heads["participation"][l] += float((nrm.sum(1) ** 2 / (nrm ** 2).sum(1)).sum())
                mx = nrm.max(1, keepdim=True).values
                heads["frac_above_10pct_of_max"][l] += float((nrm >= 0.1 * mx).double().mean(1).sum())
                heads["frac_above_50pct_of_max"][l] += float((nrm >= 0.5 * mx).double().mean(1).sum())
                heads["min_share"][l] += float(share.min(1).values.sum())
                heads["max_share"][l] += float(share.max(1).values.sum())
                head_share_sum[l] += share.sum((0, 2)).numpy()
                vp = v[:, :, NS:].double()
                v_sum[l] += vp.sum(0)
                v_sq[l] += (vp ** 2).sum((0, 2, 3))
                if l == L - 1:
                    y = (contrib.sum(1) + blk.attn.proj.bias.detach() * gam)
                    recompute_err = max(recompute_err, float((y - rec.attn[l]).abs().max()))
                    recompute_scale = max(recompute_scale, float(rec.attn[l].abs().max()))
                    sv = torch.linalg.svdvals(k.double())                     # B x H x 64
                    tol = sv.max(-1, keepdim=True).values * 261 * torch.finfo(torch.float32).eps
                    key_rank.append((sv > tol).sum(-1).numpy())
                    key_rank_1pct.append((sv > 0.01 * sv.max(-1, keepdim=True).values).sum(-1).numpy())
                    k_aug = torch.cat([k.double(), torch.ones(B, H, k.shape[2], 1, dtype=torch.float64)], -1)
                    sva = torch.linalg.svdvals(k_aug)
                    tola = sva.max(-1, keepdim=True).values * 261 * torch.finfo(torch.float32).eps
                    key_rank_aug.append((sva > tola).sum(-1).numpy())
                    key_sv.append(sv.numpy())
                del alpha, contrib, z
        n_img += B
        print(f"[{name}] {n_img}/{len(items)} images", flush=True)

    # ---- assemble
    def fdict(variant):
        ratio = f_ratio[variant] / n_tok
        pooled = f_num[variant] / f_den[variant]
        d = {}
        for tag, arr in (("mean_of_token_ratios", ratio), ("pooled", pooled)):
            d[tag] = {"f_emb": float(arr[0]), "f_attn": float(arr[1:13].sum()), "f_mlp": float(arr[13:25].sum()),
                      "sum": float(arr[:25].sum()),
                      "f_attn_per_layer": rnd(arr[1:13], 5), "f_mlp_per_layer": rnd(arr[13:25], 5),
                      "f_emb_patch_part": float(arr[25]), "f_emb_position_part": float(arr[26])}
        return d

    n_q = n_img * dino.N_PATCH
    key_rank = np.concatenate(key_rank)                                      # n_img x H
    key_rank_aug = np.concatenate(key_rank_aug)
    key_rank_1pct = np.concatenate(key_rank_1pct)
    key_sv = np.concatenate(key_sv)
    e = key_sv ** 2
    # (vii) variance of the values explained by position
    n = n_img
    v_mean_pos = v_sum / n                                                   # L x H x 256 x 64
    grand = v_mean_pos.mean(2, keepdim=True)
    total = v_sq - n * dino.N_PATCH * (grand ** 2).sum((2, 3))               # about the grand mean, per (l, h)
    between = n * ((v_mean_pos - grand) ** 2).sum((2, 3))
    res = {
        "n_images": n_img, "n_patch_tokens": n_tok,
        "i_residual_identity": {"max_abs_error": resid_err, "max_abs_x12": resid_scale,
                                "relative": resid_err / resid_scale},
        "ii_decomposition": {"raw": fdict("raw"), "centred_within_image": fdict("centred"),
                             "mean_norm_x12": float(np.concatenate(x12_norm).mean()),
                             "mean_norm_x12_centred": float(np.concatenate(x12c_norm).mean()),
                             "mean_term_norms": {"emb": float(term_norm[0] / n_tok),
                                                 "attn_per_layer": rnd(term_norm[1:13] / n_tok, 4),
                                                 "mlp_per_layer": rnd(term_norm[13:25] / n_tok, 4)}},
        "iii_last_block_recomputation": {"max_abs_diff": recompute_err, "max_abs_update": recompute_scale,
                                         "relative": recompute_err / recompute_scale},
        "iv_attention": {"entropy_nats": rnd(att["entropy"] / n_q, 4), "mean_exp_entropy": rnd(att["exp_entropy"] / n_q, 3),
                         "exp_mean_entropy": rnd(np.exp(att["entropy"] / n_q), 3),
                         "top1_mass": rnd(att["top1"] / n_q, 4), "special_tokens_mass": rnd(att["special"] / n_q, 4),
                         "self_mass": rnd(att["self"] / n_q, 4),
                         "max_entropy_ln261": float(np.log(261)), "uniform_special_mass": 5 / 261,
                         "uniform_self_mass": 1 / 261,
                         "shape": "12 blocks x 12 heads; averages over the patch-token queries of all images",
                         "per_block_mean_entropy": rnd((att["entropy"] / n_q).mean(1), 4),
                         "per_block_mean_exp_entropy": rnd((att["exp_entropy"] / n_q).mean(1), 3),
                         "per_block_mean_top1": rnd((att["top1"] / n_q).mean(1), 4),
                         "per_block_mean_special": rnd((att["special"] / n_q).mean(1), 4)},
        "v_last_block_keys": {"rank_per_head_min": key_rank.min(0).tolist(), "rank_per_head_max": key_rank.max(0).tolist(),
                              "rank_per_head_mean": rnd(key_rank.mean(0), 3),
                              "rank_of_keys_with_ones_column_max": int(key_rank_aug.max()),
                              "rank_of_keys_with_ones_column_min": int(key_rank_aug.min()),
                              "n_singular_values_above_1pct_per_head_mean": rnd(key_rank_1pct.mean(0), 2),
                              "participation_ratio_per_head_mean": rnd((e.sum(-1) ** 2 / (e ** 2).sum(-1)).mean(0), 2),
                              "tolerance": "s > s_max * 261 * eps(float32)", "matrix": "261 x 64 keys of one image",
                              "bound": "logit vectors K q span at most rank(K) <= 64 dimensions (65 with the "
                                       "softmax shift) out of m = 261"},
        "vi_heads_per_token": {k: rnd(vv / n_q, 4) for k, vv in heads.items()},
        "vi_mean_head_share": rnd(head_share_sum / n_q, 4),
        "vii_value_variance_explained_by_position": rnd((between / total).numpy(), 4),
        "vii_value_variance_explained_by_position_per_block_mean": rnd((between / total).mean(1).numpy(), 4),
    }
    return res


def main():
    t0 = time.time()
    torch.set_num_threads(4)
    stat, _ = dino.imagenette_lists()
    items = [it for i, it in enumerate(stat) if (i % 100) < N_PER_CLASS]
    out = {"experiment": "R4 attention anatomy", "images": f"first {N_PER_CLASS} statistics images of each class (100)",
           "layerscale_note": "trained model: LayerScale gammas are learned; random twin: all equal to 1"}
    for name, pretrained in (("trained", True), ("random_twin", False)):
        model = dino.load_model(pretrained, seed=0)
        out[name] = run(model, items, name)
        r = out[name]
        d = r["ii_decomposition"]
        print(f"== {name}: residual identity err {r['i_residual_identity']['max_abs_error']:.2e} "
              f"(max |x12| {r['i_residual_identity']['max_abs_x12']:.1f}); last-block recomputation diff "
              f"{r['iii_last_block_recomputation']['max_abs_diff']:.2e} (max |update| "
              f"{r['iii_last_block_recomputation']['max_abs_update']:.2f})")
        for variant in ("raw", "centred_within_image"):
            m = d[variant]["mean_of_token_ratios"]
            print(f"   {variant}: f_emb {m['f_emb']:.4f} f_attn {m['f_attn']:.4f} f_mlp {m['f_mlp']:.4f} (sum {m['sum']:.6f})")
            print("      attn/layer", m["f_attn_per_layer"])
            print("      mlp/layer ", m["f_mlp_per_layer"])
        a = r["iv_attention"]
        print("   entropy per block (mean over heads):", a["per_block_mean_entropy"], "max", round(a["max_entropy_ln261"], 3))
        print("   mean exp(entropy) per block:", a["per_block_mean_exp_entropy"])
        print("   top-1 mass per block:", a["per_block_mean_top1"])
        print("   special-token mass per block:", a["per_block_mean_special"])
        print("   last-block key rank per head (min..max):", r["v_last_block_keys"]["rank_per_head_min"],
              r["v_last_block_keys"]["rank_per_head_max"], "| with ones column max",
              r["v_last_block_keys"]["rank_of_keys_with_ones_column_max"])
        print("   heads per token: participation", r["vi_heads_per_token"]["participation"])
        print("   frac heads >= 10% of max:", r["vi_heads_per_token"]["frac_above_10pct_of_max"])
        print("   value variance explained by position (block mean):", r["vii_value_variance_explained_by_position_per_block_mean"])
        save_json("r4_attention_anatomy", out, t0)
        del model


if __name__ == "__main__":
    main()
