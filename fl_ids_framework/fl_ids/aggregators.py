"""Aggregation rules on flattened parameter vectors (one row per client).

All rules are joint over the whole parameter vector, as in thesis Algorithm 3.
Weights are used by fedavg and geometric_median only; the other rules are unweighted,
as in the thesis's comparison tables.
"""
from __future__ import annotations

import time

import numpy as np

AGGREGATORS = ("fedavg", "geometric_median", "krum", "multi_krum", "trimmed_mean", "median")


def _weights(n: int, w) -> np.ndarray:
    if w is None:
        return np.full(n, 1.0 / n)
    w = np.clip(np.asarray(w, dtype=np.float64), 0.0, None)
    if w.sum() <= 0:
        return np.full(n, 1.0 / n)
    return w / w.sum()


def fedavg(U: np.ndarray, w=None):
    return _weights(U.shape[0], w) @ U, {}


def geometric_median(U: np.ndarray, w=None, max_iter: int = 200, tol: float = 1e-7, eps: float = 1e-10):
    """Weighted geometric median by Weiszfeld's algorithm (thesis Algorithm 3).

    Starts from the weighted mean; each step re-weights clients by w_i / ||u_i - y||.
    """
    w = _weights(U.shape[0], w)
    y = w @ U
    it = 0
    for it in range(1, max_iter + 1):
        d = np.maximum(np.linalg.norm(U - y, axis=1), eps)
        c = w / d
        y_new = (c @ U) / c.sum()
        moved = np.linalg.norm(y_new - y)
        y = y_new
        if moved <= tol * max(1.0, np.linalg.norm(y)):
            break
    return y, {"iterations": it}


def coordinate_median(U: np.ndarray, w=None):
    return np.median(U, axis=0), {}


def trimmed_mean(U: np.ndarray, ratio: float = 0.1):
    n = U.shape[0]
    t = int(np.floor(ratio * n))
    if 2 * t >= n:
        return np.median(U, axis=0), {"fallback": "median"}
    S = np.sort(U, axis=0)
    return S[t:n - t].mean(axis=0), {"trimmed_each_side": t}


def _pairwise_sq_dists(U: np.ndarray) -> np.ndarray:
    G = U @ U.T
    s = np.diag(G)
    D = s[:, None] + s[None, :] - 2.0 * G
    np.maximum(D, 0.0, out=D)
    np.fill_diagonal(D, np.inf)
    return D


def krum(U: np.ndarray, f: int, multi: bool = False):
    """Krum (Blanchard et al. 2017): pick the update closest to its n-f-2 nearest neighbours."""
    n = U.shape[0]
    k = n - f - 2
    if k < 1:
        vec, _ = fedavg(U)
        return vec, {"fallback": "fedavg"}
    scores = np.sort(_pairwise_sq_dists(U), axis=1)[:, :k].sum(axis=1)
    if multi:
        m = max(1, n - f)
        chosen = np.argsort(scores)[:m]
        return U[chosen].mean(axis=0), {"selected": chosen.tolist()}
    i = int(np.argmin(scores))
    return U[i].copy(), {"selected": [i]}


def aggregate(name: str, U: np.ndarray, weights=None, f: int = 0, trim_ratio: float = 0.1):
    """Dispatch by name. Returns (aggregated vector, info dict with 'seconds')."""
    t0 = time.perf_counter()
    if name == "fedavg":
        vec, info = fedavg(U, weights)
    elif name == "geometric_median":
        vec, info = geometric_median(U, weights)
    elif name == "krum":
        vec, info = krum(U, f, multi=False)
    elif name == "multi_krum":
        vec, info = krum(U, f, multi=True)
    elif name == "trimmed_mean":
        vec, info = trimmed_mean(U, trim_ratio)
    elif name == "median":
        vec, info = coordinate_median(U)
    else:
        raise ValueError(f"unknown aggregator {name!r}")
    info = dict(info)
    info["seconds"] = time.perf_counter() - t0
    return vec, info
