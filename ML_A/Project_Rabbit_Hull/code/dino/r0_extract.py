"""R0 — feature extraction and caches (run once; everything else reads the cache).

Writes into <cache>/feats/ (outside the repository):
  trained_prenorm.npy, trained_postnorm.npy   1000 x 256 x 768 float32, final-layer patch tokens of the 1000
                                              statistics images, before / after the final LayerNorm
  random_prenorm.npy, random_postnorm.npy     the same for the random-weights twin (seed 0)
  trained_special_postnorm.npy                1000 x 5 x 768, cls + 4 register tokens after the final LayerNorm
  trained_layer_stats.npz                     per-layer sufficient statistics for R7 (position means, second
                                              moments, normal equations of the position probe on 300 images)
  heldout_layers_f16.npy                      14 x 100 x 256 x 768 float16: patch tokens of 100 held-out images
                                              at the 13 residual-stream depths and after the final LayerNorm
and into code/results/:
  r0_image_lists.json                         the fixed image lists (file names), versions, timings

Layer index convention ("depth"): 0 = input of block 1 (patch embedding + position embedding), l = 1..12 =
output of block l, 13 = output of the final LayerNorm applied to depth 12.
"""
import json
import os
import sys
import time

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from rh import dino  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
N_TRAIN_PER_CLASS = 30      # images per class whose tokens enter the normal equations of the position probe
N_HELD_PER_CLASS = 10       # held-out images per class stored for the probe test
BS = 20


def depth_states(rec, model, out):
    """List of the 14 states (B x 261 x 768): residual stream at depths 0..12, then the final LayerNorm."""
    states = [rec.x_in[0]] + [rec.x_out[l] for l in range(12)]
    x_norm = torch.cat([out["x_norm_clstoken"][:, None], out["x_norm_regtokens"], out["x_norm_patchtokens"]], 1)
    return states + [x_norm]


def run_pass(model, items, name, cache_dir, layer_stats=False, log=print):
    N = len(items)
    os.makedirs(os.path.join(cache_dir, "feats"), exist_ok=True)
    pre = np.lib.format.open_memmap(dino.feature_path(f"{name}_prenorm", cache_dir), mode="w+",
                                    dtype=np.float32, shape=(N, dino.N_PATCH, dino.DIM))
    post = np.lib.format.open_memmap(dino.feature_path(f"{name}_postnorm", cache_dir), mode="w+",
                                     dtype=np.float32, shape=(N, dino.N_PATCH, dino.DIM))
    special = np.zeros((N, dino.N_SPECIAL, dino.DIM), dtype=np.float32)
    L = 14
    if layer_stats:
        pos_sum = torch.zeros(L, 261, dino.DIM, dtype=torch.float64)      # sum over images, per token position
        sq_sum = torch.zeros(L, dtype=torch.float64)                      # sum of ||x||^2 over patch tokens
        xtx = torch.zeros(L, dino.DIM, dino.DIM, dtype=torch.float64)     # train images, patch tokens
        pos_sum_train = torch.zeros(L, dino.N_PATCH, dino.DIM, dtype=torch.float64)
        n_train = 0
    t0 = time.time()
    for b in range(0, N, BS):
        x = dino.load_batch(items[b:b + BS])
        with torch.no_grad(), dino.Recorder(model) as rec:
            out = model.forward_features(x)
            pre[b:b + BS] = out["x_prenorm"][:, dino.N_SPECIAL:].numpy()
            post[b:b + BS] = out["x_norm_patchtokens"].numpy()
            special[b:b + BS, 0] = out["x_norm_clstoken"].numpy()
            special[b:b + BS, 1:] = out["x_norm_regtokens"].numpy()
            if layer_stats:
                idx = np.arange(b, min(b + BS, N))
                is_train = torch.from_numpy((idx % 100) < N_TRAIN_PER_CLASS)
                for l, s in enumerate(depth_states(rec, model, out)):
                    s64 = s.double()
                    pos_sum[l] += s64.sum(0)
                    sq_sum[l] += (s64[:, dino.N_SPECIAL:] ** 2).sum()
                    if is_train.any():
                        tr = s64[is_train][:, dino.N_SPECIAL:]
                        pos_sum_train[l] += tr.sum(0)
                        flat = tr.reshape(-1, dino.DIM)
                        xtx[l] += flat.T @ flat
                n_train += int(is_train.sum())
        if (b // BS) % 5 == 0:
            log(f"[{name}] {b + len(x)}/{N} images, {time.time() - t0:.0f} s")
    pre.flush()
    post.flush()
    del pre, post
    if name == "trained":
        np.save(dino.feature_path("trained_special_postnorm", cache_dir), special)
    if layer_stats:
        np.savez(os.path.join(cache_dir, "feats", f"{name}_layer_stats.npz"),
                 pos_sum=pos_sum.numpy(), sq_sum=sq_sum.numpy(), xtx_train=xtx.numpy(),
                 pos_sum_train=pos_sum_train.numpy(), n_images=N, n_train_images=n_train,
                 depth_labels=np.array([f"{l}" for l in range(13)] + ["12+LN"]))
    return time.time() - t0


def heldout_pass(model, items, cache_dir, log=print):
    out_arr = np.lib.format.open_memmap(dino.feature_path("heldout_layers_f16", cache_dir), mode="w+",
                                        dtype=np.float16, shape=(14, len(items), dino.N_PATCH, dino.DIM))
    t0 = time.time()
    for b in range(0, len(items), BS):
        x = dino.load_batch(items[b:b + BS])
        with torch.no_grad(), dino.Recorder(model) as rec:
            out = model.forward_features(x)
            for l, s in enumerate(depth_states(rec, model, out)):
                out_arr[l, b:b + BS] = s[:, dino.N_SPECIAL:].numpy().astype(np.float16)
    out_arr.flush()
    log(f"[heldout] {len(items)} images, {time.time() - t0:.0f} s")
    return time.time() - t0


def main(cache_dir=dino.DEFAULT_CACHE):
    torch.set_num_threads(4)
    stat, held = dino.imagenette_lists(cache_dir)
    held_probe = [it for i, it in enumerate(held) if (i % 20) < N_HELD_PER_CLASS]
    meta = {"versions": dino.versions(cache_dir), "dataset": dino.IMAGENETTE_URL,
            "preprocessing": "resize shorter side to 256 (PIL bicubic), centre crop 224, ImageNet mean/std",
            "stat_images": [os.path.join(os.path.basename(os.path.dirname(p)), os.path.basename(p)) for p, _ in stat],
            "stat_labels": [c for _, c in stat],
            "heldout_images": [os.path.join(os.path.basename(os.path.dirname(p)), os.path.basename(p)) for p, _ in held],
            "heldout_labels": [c for _, c in held],
            "probe_train": f"first {N_TRAIN_PER_CLASS} statistics images of each class",
            "probe_test": f"first {N_HELD_PER_CLASS} held-out images of each class",
            "random_twin": "pretrained=False after torch.manual_seed(0)", "timings_s": {}}
    flag = os.path.join(cache_dir, "feats", "{}.done")
    if not os.path.exists(flag.format("trained")):
        model = dino.load_model(True, cache_dir=cache_dir)
        meta["timings_s"]["trained"] = run_pass(model, stat, "trained", cache_dir, layer_stats=True)
        meta["timings_s"]["heldout"] = heldout_pass(model, held_probe, cache_dir)
        open(flag.format("trained"), "w").write("ok")
        del model
    if not os.path.exists(flag.format("random")):
        twin = dino.load_model(False, seed=0, cache_dir=cache_dir)
        meta["timings_s"]["random"] = run_pass(twin, stat, "random", cache_dir, layer_stats=False)
        open(flag.format("random"), "w").write("ok")
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "r0_image_lists.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print("R0 done", meta["timings_s"])


if __name__ == "__main__":
    main()
