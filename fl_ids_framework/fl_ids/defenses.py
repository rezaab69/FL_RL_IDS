"""Server-side defences: quality gate, anomaly filter, exclusion and client weighting.

Order used by the federation (thesis Algorithm 1 and Section 7-3):
  quality gate (local accuracy or F1 >= threshold)
  -> anomaly filter over the clients that passed the gate (Z-score or IQR)
  -> exclusion after a number of consecutive failures
  -> weighting (F1, accuracy or data size) and aggregation
"""
from __future__ import annotations

import numpy as np

from .config import FedConfig


def quality_passes(metrics: dict, cfg: FedConfig) -> bool:
    if cfg.gate == "none":
        return True
    value = metrics["accuracy"] if cfg.gate == "accuracy" else metrics["f1"]
    return value >= cfg.gate_threshold


def anomaly_flags(V: np.ndarray, cfg: FedConfig) -> np.ndarray:
    """V has one row per client. Returns a boolean flag per client.

    A client is flagged when more than anomaly_fraction of its parameters are outliers
    (|Z| > anomaly_limit for zscore, or outside the 1.5*IQR fences for iqr).
    """
    n = V.shape[0]
    if cfg.anomaly_filter == "none" or n < 3:
        return np.zeros(n, dtype=bool)
    if cfg.anomaly_filter == "zscore":
        mu = V.mean(axis=0)
        sd = V.std(axis=0)
        sd = np.where(sd > 0, sd, np.inf)              # constant parameters give Z = 0
        outlier = np.abs((V - mu) / sd) > cfg.anomaly_limit
    elif cfg.anomaly_filter == "iqr":
        q1, q3 = np.percentile(V, [25, 75], axis=0)
        iqr = q3 - q1
        outlier = (V < q1 - 1.5 * iqr) | (V > q3 + 1.5 * iqr)
    else:
        raise ValueError(f"unknown anomaly filter {cfg.anomaly_filter!r}")
    return outlier.mean(axis=1) > cfg.anomaly_fraction


class ExclusionTracker:
    """A client is suspended after `patience` consecutive failed rounds and readmitted on a pass."""

    def __init__(self, patience: int):
        self.patience = patience
        self.failures: dict = {}
        self.suspended: set = set()

    def record(self, cid: int, passed: bool) -> None:
        if self.patience <= 0:
            return
        if passed:
            self.failures[cid] = 0
            self.suspended.discard(cid)
        else:
            self.failures[cid] = self.failures.get(cid, 0) + 1
            if self.failures[cid] >= self.patience:
                self.suspended.add(cid)

    def is_suspended(self, cid: int) -> bool:
        return cid in self.suspended


def minmax(x) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    span = x.max() - x.min()
    return (x - x.min()) / span if span > 0 else np.zeros_like(x)


def client_weights(mode: str, f1s, accs, sizes) -> np.ndarray:
    """Relative weights of the included clients. 'none' gives equal weights."""
    n = len(sizes)
    if mode == "none":
        return np.ones(n)
    table = {
        "f1": np.asarray(f1s, float),
        "accuracy": np.asarray(accs, float),
        "datasize": np.asarray(sizes, float),
    }
    if mode.endswith("_minmax"):
        base = minmax(table[mode[: -len("_minmax")]])
    elif mode in table:
        base = table[mode]
    else:
        raise ValueError(f"unknown weighting {mode!r}")
    return base if base.sum() > 0 else np.ones(n)
