"""R3b: within-image variance of the final-layer (post-norm) patch tokens.

Converts the fractions of variance unexplained (FVU) of R3, which are relative to the variance of the
tokens of one image about their mean, into mean squared errors per coordinate, the unit of the paper's
Fig. 17 (middle):  MSE per coordinate = FVU x (within-image variance per token) / d.

Run from code/:  python dino/r3b_within_variance.py [--cache DIR]
"""
import argparse, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CACHE = "/tmp/claude-0/-home-user-MVA-courses/0bf8c9d0-cffb-55d5-b9e4-5992de5f6b3a/scratchpad/lab_cache"

ap = argparse.ArgumentParser()
ap.add_argument("--cache", default=DEFAULT_CACHE)
args = ap.parse_args()

X = np.load(os.path.join(args.cache, "feats", "trained_postnorm.npy"), mmap_mode="r")  # (1000, 256, 768)
idx = [c * 100 + j for c in range(10) for j in range(20)]  # the 200 images of R3 ("post")
d = X.shape[-1]
within = []
for i in idx:
    x = np.asarray(X[i], dtype=np.float64)
    within.append(((x - x.mean(0)) ** 2).sum() / x.shape[0])
within = np.array(within)
pooled = np.asarray(X[idx], dtype=np.float64).reshape(-1, d)
total = ((pooled - pooled.mean(0)) ** 2).sum() / pooled.shape[0]
out = {
    "experiment": "R3b within-image variance of post-norm patch tokens (the 200 images of R3)",
    "n_images": len(idx), "d": int(d),
    "within_image_variance_per_token_mean": float(within.mean()),
    "within_image_variance_per_token_sd": float(within.std()),
    "within_image_variance_per_coordinate": float(within.mean() / d),
    "total_variance_per_token": float(total),
    "total_variance_per_coordinate": float(total / d),
    "within_over_total": float(within.mean() / total),
}
with open(os.path.join(HERE, "..", "results", "r3_within_variance.json"), "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1))
