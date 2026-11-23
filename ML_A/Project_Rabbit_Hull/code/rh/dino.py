"""DINOv2 loading, preprocessing, hooks and feature caching (needs torch, torchvision, pillow).

Model: DINOv2 ViT-B/14 with 4 registers (``dinov2_vitb14_reg`` of facebookresearch/dinov2, LVD-142M weights).
d = 768, 12 blocks, 12 heads of dimension 64; for a 224 x 224 input the token order is
[cls, 4 registers, 256 patches] (16 x 16 grid, row-major).

Everything large (code of the hub repository, weights, datasets, cached features) lives in a cache directory
outside the repository; every function takes it as ``cache_dir`` and defaults to ``DEFAULT_CACHE`` (which the
environment variable ``RH_CACHE`` overrides).
"""
from __future__ import annotations

import os
import sys
import warnings

import numpy as np

DEFAULT_CACHE = os.environ.get(
    "RH_CACHE",
    "/tmp/claude-0/-home-user-MVA-courses/0bf8c9d0-cffb-55d5-b9e4-5992de5f6b3a/scratchpad/lab_cache",
)

MODEL_NAME = "dinov2_vitb14_reg"
WEIGHTS_FILE = "dinov2_vitb14_reg4_pretrain.pth"
WEIGHTS_URL = "https://dl.fbaipublicfiles.com/dinov2/dinov2_vitb14/" + WEIGHTS_FILE
MODEL_ID = ("facebookresearch/dinov2 hub entry 'dinov2_vitb14_reg' (ViT-B/14, 4 registers, LVD-142M), "
            "weights " + WEIGHTS_URL)
IMAGENETTE_URL = "https://s3.amazonaws.com/fast-ai-imageclassification/imagenette2-320.tgz"
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
N_SPECIAL = 5            # cls + 4 registers
N_PATCH = 256            # 16 x 16
GRID = 16
DIM = 768

__all__ = ["DEFAULT_CACHE", "MODEL_ID", "load_model", "preprocess", "preprocess_pil", "imagenette_lists",
           "load_batch", "Recorder", "attention_parts", "final_norm_params", "feature_path", "load_features",
           "versions", "N_SPECIAL", "N_PATCH", "GRID", "DIM"]


# --------------------------------------------------------------------------------------------------------------
# versions (recorded in every results file)
# --------------------------------------------------------------------------------------------------------------
def versions(cache_dir=DEFAULT_CACHE):
    """Package versions, model identifier and checksum of the weight file."""
    import hashlib
    import platform
    out = {"python": platform.python_version(), "numpy": np.__version__, "model": MODEL_ID}
    for name in ("torch", "torchvision", "scipy", "sklearn", "skimage", "PIL"):
        try:
            mod = __import__(name)
            out[name] = getattr(mod, "__version__", "?")
        except Exception:                                       # pragma: no cover
            out[name] = None
    w = os.path.join(cache_dir, "torch_home", "hub", "checkpoints", WEIGHTS_FILE)
    sha_file = w + ".sha256"
    if os.path.exists(sha_file):
        out["weights_sha256"] = open(sha_file).read().strip()
    elif os.path.exists(w):
        h = hashlib.sha256()
        with open(w, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 22), b""):
                h.update(chunk)
        out["weights_sha256"] = h.hexdigest()
        try:
            open(sha_file, "w").write(out["weights_sha256"])
        except OSError:
            pass
    out["model_code"] = ("python sources of facebookresearch/dinov2 (branch main, fetched 2026-11-23 from "
                         "raw.githubusercontent.com), loaded with torch.hub.load(<local copy>, source='local')")
    return out


# --------------------------------------------------------------------------------------------------------------
# model
# --------------------------------------------------------------------------------------------------------------
def load_model(pretrained=True, seed=0, cache_dir=DEFAULT_CACHE, n_threads=None):
    """DINOv2 ViT-B/14 with registers, in eval mode.

    ``pretrained=False`` gives the random-weights twin: same architecture, parameters drawn by the model's own
    initialisation after ``torch.manual_seed(seed)`` (LayerScale at its initial value 1).

    The hub repository is used from a local copy ``<cache_dir>/dinov2_repo`` when it exists (the sandbox of this
    project cannot reach github.com), otherwise ``torch.hub`` downloads it.
    """
    import torch
    if n_threads:
        torch.set_num_threads(int(n_threads))
    torch.hub.set_dir(os.path.join(cache_dir, "torch_home", "hub"))
    repo = os.path.join(cache_dir, "dinov2_repo")
    if not pretrained:
        torch.manual_seed(seed)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")                         # "xFormers is not available" (x3)
        if os.path.exists(os.path.join(repo, "hubconf.py")):
            model = torch.hub.load(repo, MODEL_NAME, source="local", pretrained=pretrained)
        else:
            model = torch.hub.load("facebookresearch/dinov2", MODEL_NAME, pretrained=pretrained)
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    assert model.embed_dim == DIM and len(model.blocks) == 12 and model.num_register_tokens == 4
    return model


def final_norm_params(model):
    """(gamma, beta, eps) of the final LayerNorm, as float64 numpy arrays."""
    return (model.norm.weight.detach().double().numpy().copy(),
            model.norm.bias.detach().double().numpy().copy(), float(model.norm.eps))


# --------------------------------------------------------------------------------------------------------------
# data
# --------------------------------------------------------------------------------------------------------------
def preprocess_pil(img, crop=224, resize=256):
    """Resize the shorter side to ``resize`` (bicubic) and centre-crop ``crop``: returns a PIL RGB image."""
    from PIL import Image
    img = img.convert("RGB")
    w, h = img.size
    s = resize / min(w, h)
    nw, nh = max(resize, int(round(w * s))), max(resize, int(round(h * s)))
    img = img.resize((nw, nh), Image.BICUBIC)
    left, top = (nw - crop) // 2, (nh - crop) // 2
    return img.crop((left, top, left + crop, top + crop))


def preprocess(img):
    """PIL image -> normalised float32 tensor 3 x 224 x 224 (ImageNet mean / std)."""
    import torch
    arr = np.asarray(preprocess_pil(img), dtype=np.float32) / 255.0
    arr = (arr - np.array(IMAGENET_MEAN, dtype=np.float32)) / np.array(IMAGENET_STD, dtype=np.float32)
    return torch.from_numpy(np.ascontiguousarray(arr.transpose(2, 0, 1)))


def imagenette_lists(cache_dir=DEFAULT_CACHE, n_stat=100, n_held=20):
    """Fixed image lists from the Imagenette validation split.

    Returns ``(stat, held)``: lists of (path, class_index). ``stat`` = first ``n_stat`` file names (sorted) of
    each of the 10 classes (class-major order: image index // n_stat = class); ``held`` = the next ``n_held``.
    """
    root = os.path.join(cache_dir, "data", "untar", "imagenette2-320", "val")
    if not os.path.isdir(root):
        raise FileNotFoundError(f"Imagenette not found under {root}; download and untar {IMAGENETTE_URL} "
                                f"into {os.path.join(cache_dir, 'data', 'untar')}")
    classes = sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))
    stat, held = [], []
    for ci, c in enumerate(classes):
        files = sorted(os.listdir(os.path.join(root, c)))
        assert len(files) >= n_stat + n_held
        stat += [(os.path.join(root, c, f), ci) for f in files[:n_stat]]
        held += [(os.path.join(root, c, f), ci) for f in files[n_stat:n_stat + n_held]]
    return stat, held


def load_batch(items):
    """List of (path, label) or of paths -> float32 tensor B x 3 x 224 x 224."""
    import torch
    from PIL import Image
    out = []
    for it in items:
        path = it[0] if isinstance(it, (tuple, list)) else it
        with Image.open(path) as im:
            out.append(preprocess(im))
    return torch.stack(out)


# --------------------------------------------------------------------------------------------------------------
# hooks
# --------------------------------------------------------------------------------------------------------------
class Recorder:
    """Forward hooks on every block of the model. Use as a context manager around ``model.forward_features``.

    After a forward pass (all tensors B x 261 x 768, detached):
      ``x_in[l]``    input of block l (l = 0..11); ``x_in[0]`` is the embedding (patch + position, cls, registers)
      ``x_out[l]``   output of block l
      ``attn[l]``    attention-branch update, after LayerScale:  ls1(attn(norm1(x)))
      ``mlp[l]``     MLP-branch update, after LayerScale:        ls2(mlp(norm2(x + attn)))
      ``attn_in[l]`` input of the attention module (= norm1(x)), only with ``attn_inputs=True``
    so that  x_out[l] = x_in[l] + attn[l] + mlp[l]  and  x_in[l + 1] = x_out[l].
    """

    def __init__(self, model, attn_inputs=False):
        self.model = model
        self.attn_inputs = attn_inputs
        self.handles = []
        self.clear()

    def clear(self):
        n = len(self.model.blocks)
        self.x_in = [None] * n
        self.x_out = [None] * n
        self.attn = [None] * n
        self.mlp = [None] * n
        self.attn_in = [None] * n

    def __enter__(self):
        for l, blk in enumerate(self.model.blocks):
            def blk_hook(mod, inp, out, l=l):
                self.x_in[l] = inp[0].detach()
                self.x_out[l] = out.detach()

            def ls1_hook(mod, inp, out, l=l):
                self.attn[l] = out.detach()

            def ls2_hook(mod, inp, out, l=l):
                self.mlp[l] = out.detach()

            self.handles.append(blk.register_forward_hook(blk_hook))
            self.handles.append(blk.ls1.register_forward_hook(ls1_hook))
            self.handles.append(blk.ls2.register_forward_hook(ls2_hook))
            if self.attn_inputs:
                def attn_hook(mod, inp, out, l=l):
                    self.attn_in[l] = inp[0].detach()
                self.handles.append(blk.attn.register_forward_hook(attn_hook))
        return self

    def __exit__(self, *exc):
        for h in self.handles:
            h.remove()
        self.handles = []
        return False


def attention_parts(blk, h):
    """Recompute the pieces of a block's attention from the input ``h`` of its attention module (= norm1(x)).

    Returns ``(alpha, v, q, k)`` with alpha = softmax(q k^T / sqrt(64)) of shape B x H x N x N (rows = queries)
    and q, k, v of shape B x H x N x 64.
    """
    import torch
    attn = blk.attn
    B, N, C = h.shape
    H = attn.num_heads
    qkv = attn.qkv(h).reshape(B, N, 3, H, C // H)
    q, k, v = [t.transpose(1, 2) for t in torch.unbind(qkv, 2)]
    logits = (q @ k.transpose(-1, -2)) * attn.scale
    alpha = torch.softmax(logits, dim=-1)
    return alpha, v, q, k


# --------------------------------------------------------------------------------------------------------------
# feature cache
# --------------------------------------------------------------------------------------------------------------
def feature_path(name, cache_dir=DEFAULT_CACHE):
    """Path of a cached array, e.g. ``trained_postnorm`` -> <cache>/feats/trained_postnorm.npy."""
    return os.path.join(cache_dir, "feats", name + ".npy")


def load_features(which="trained", kind="postnorm", cache_dir=DEFAULT_CACHE, mmap=True):
    """Final-layer patch tokens of the 1000 statistics images: array 1000 x 256 x 768 (float32).

    ``which`` in {"trained", "random"}; ``kind`` in {"postnorm" (x_norm_patchtokens), "prenorm" (patch rows of
    x_prenorm)}. Written by ``code/dino/r0_extract.py``.
    """
    path = feature_path(f"{which}_{kind}", cache_dir)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} is missing: run code/dino/r0_extract.py first")
    return np.load(path, mmap_mode="r" if mmap else None)


def add_code_path():
    """Make ``import rh`` work when a script of code/dino is run directly."""
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if here not in sys.path:
        sys.path.insert(0, here)
