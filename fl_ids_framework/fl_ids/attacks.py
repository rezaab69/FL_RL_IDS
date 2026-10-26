"""Poisoning attacks: label flipping (data poisoning) and update manipulation (model poisoning).

label_flip      the malicious client flips a fraction of its training labels (thesis: 50%)
model_noise     the malicious client sends its parameters plus Gaussian noise (thesis: std 10)
sign_flip       the malicious client sends global - (local - global)
scaling         the malicious client sends global + k * (local - global)
"""
from __future__ import annotations

import numpy as np

from .config import AttackConfig


def select_malicious(n_clients: int, n_malicious: int, rng: np.random.Generator) -> set:
    if n_malicious <= 0:
        return set()
    if n_malicious > n_clients:
        raise ValueError("more malicious clients than clients")
    return set(int(i) for i in rng.choice(n_clients, size=n_malicious, replace=False))


def flip_labels(y: np.ndarray, fraction: float, n_classes: int, rng: np.random.Generator) -> np.ndarray:
    """Binary tasks flip 0<->1. Multiclass tasks move each chosen label to a different class."""
    y = y.copy()
    k = int(round(fraction * len(y)))
    idx = rng.choice(len(y), size=k, replace=False)
    if n_classes == 2:
        y[idx] = 1 - y[idx]
    else:
        shift = rng.integers(1, n_classes, size=k)
        y[idx] = (y[idx] + shift) % n_classes
    return y


def manipulate_update(local: np.ndarray, global_vec: np.ndarray, cfg: AttackConfig,
                      rng: np.random.Generator) -> np.ndarray:
    """The vector a malicious client sends instead of its honest parameters."""
    if cfg.kind == "model_noise":
        return local + rng.normal(0.0, cfg.noise_std, size=local.shape)
    if cfg.kind == "sign_flip":
        return global_vec - (local - global_vec)
    if cfg.kind == "scaling":
        return global_vec + cfg.scale_factor * (local - global_vec)
    return local
