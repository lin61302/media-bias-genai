"""Read the public, hash-pinned aggregate snapshot. No article or model access."""
from pathlib import Path
import hashlib
import json
from urllib.request import urlopen
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
LABELS = np.array([-1, 0, 1])
AXES = ("align", "rep", "frame")


def load(name):
    manifest = json.loads((ROOT / "data/analysis_snapshot.json").read_text())
    spec = manifest["files"][name]
    target = ROOT / "data/cache" / name
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        with urlopen(spec["url"], timeout=120) as response:
            body = response.read()
        if hashlib.sha256(body).hexdigest() != spec["sha256"]:
            raise ValueError("Downloaded file differs from the pinned snapshot: " + name)
        target.write_bytes(body)
    body = target.read_bytes()
    if hashlib.sha256(body).hexdigest() != spec["sha256"]:
        raise ValueError("Cached file differs from the pinned snapshot: " + name)
    return json.loads(body)


def cube(row):
    a = np.asarray(row["c"], dtype=np.int64)
    if a.shape != (27,) or np.any(a < 0):
        raise ValueError("Expected 27 nonnegative joint counts")
    return a.reshape(3, 3, 3)


def marginal(row, axis):
    axis = AXES.index(axis) if isinstance(axis, str) else axis
    a = cube(row)
    return a.sum(axis=tuple(i for i in range(3) if i != axis))


def measures(row, axis):
    a = marginal(row, axis)
    n = int(a.sum())
    neg, zero, pos = a / n if n else [np.nan] * 3
    return dict(n=n, negative=neg, zero=zero, positive=pos,
                net=pos-neg, two_sided=4*pos*neg)


def correlation(row, a="align", b="rep"):
    a, b = AXES.index(a), AXES.index(b)
    if a == b:
        raise ValueError("Choose two different fields")
    c = cube(row)
    x = np.indices(c.shape)[a] - 1
    y = np.indices(c.shape)[b] - 1
    n = c.sum()
    if not n:
        return np.nan
    mx, my = (c*x).sum()/n, (c*y).sum()/n
    vx, vy = (c*(x-mx)**2).sum()/n, (c*(y-my)**2).sum()/n
    return (c*(x-mx)*(y-my)).sum()/n/np.sqrt(vx*vy) if vx*vy > 0 else np.nan


def radius(n, equal=False):
    """Dashboard radius in SVG coordinates; circle area is NOT proportional to n."""
    return 6.0 if equal else 4 + min(12, np.sqrt(n)/30)
