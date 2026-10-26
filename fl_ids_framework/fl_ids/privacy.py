"""Differential-privacy mechanism (Gaussian) and L2 clipping of client updates.

sigma = sqrt(2 ln(1.25/delta)) * sensitivity / epsilon   (classic Gaussian mechanism)

target="update": the client clips its update (local - global) to C and adds noise to the
clipped update, so the sensitivity is C. This is the standard calibration.

target="parameters": noise is added to the raw parameter vector, as the thesis's Algorithm 4
literally states. The sensitivity is then only a convention (default C).
"""
from __future__ import annotations

import math

import numpy as np

from .config import PrivacyConfig


def gaussian_sigma(epsilon: float, delta: float, sensitivity: float) -> float:
    if epsilon <= 0 or not 0 < delta < 1:
        raise ValueError("need epsilon > 0 and 0 < delta < 1")
    return math.sqrt(2.0 * math.log(1.25 / delta)) * sensitivity / epsilon


def clip_l2(v: np.ndarray, c: float) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if c is None or n <= c or n == 0.0:
        return v
    return v * (c / n)


def protect(local: np.ndarray, global_vec: np.ndarray, cfg: PrivacyConfig, rng: np.random.Generator):
    """Return (vector to send, noise standard deviation used)."""
    sensitivity = cfg.sensitivity if cfg.sensitivity is not None else cfg.clip_norm
    sigma = gaussian_sigma(cfg.epsilon, cfg.delta, sensitivity)
    if cfg.target == "update":
        update = clip_l2(local - global_vec, cfg.clip_norm)
        out = global_vec + update + rng.normal(0.0, sigma, size=local.shape)
    elif cfg.target == "parameters":
        out = local + rng.normal(0.0, sigma, size=local.shape)
    else:
        raise ValueError(f"unknown DP target {cfg.target!r}")
    return out, sigma
