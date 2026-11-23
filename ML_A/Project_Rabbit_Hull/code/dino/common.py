"""Small helpers shared by the R-scripts (paths, JSON output, summaries)."""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.dirname(HERE)
RESULTS = os.path.join(CODE, "results")
if CODE not in sys.path:
    sys.path.insert(0, CODE)

from rh import dino  # noqa: E402

QUICKLOOK = os.path.join(os.path.dirname(dino.DEFAULT_CACHE), "lab_quicklook")


def summ(x, digits=6):
    """Distribution summary of an array: mean, std, min, quartiles, max, n."""
    x = np.asarray(x, dtype=np.float64).ravel()
    q = np.quantile(x, [0.0, 0.25, 0.5, 0.75, 1.0])
    out = {"mean": x.mean(), "std": x.std(), "min": q[0], "q25": q[1], "median": q[2], "q75": q[3], "max": q[4]}
    out = {k: float(np.round(v, digits)) for k, v in out.items()}
    out["n"] = int(x.size)
    return out


def mean_sem(x, axis=0):
    x = np.asarray(x, dtype=np.float64)
    n = x.shape[axis]
    return x.mean(axis), x.std(axis, ddof=1) / np.sqrt(n) if n > 1 else np.zeros_like(x.mean(axis))


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return jsonable(o.tolist())
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, float) and not np.isfinite(o):
        return None
    return o


def save_json(name, obj, t0=None):
    """Write code/results/<name>.json with the versions block added."""
    os.makedirs(RESULTS, exist_ok=True)
    obj = dict(obj)
    obj.setdefault("versions", dino.versions())
    obj.setdefault("written", time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
    if t0 is not None:
        obj.setdefault("runtime_s", round(time.time() - t0, 1))
    path = os.path.join(RESULTS, name + ".json")
    with open(path, "w") as f:
        json.dump(jsonable(obj), f, indent=1)
    print(f"wrote {path} ({os.path.getsize(path) / 1024:.0f} kB)")
    return path


def rnd(a, digits=5):
    """Rounded nested list of a float array (keeps JSON files small)."""
    return np.round(np.asarray(a, dtype=np.float64), digits).tolist()
