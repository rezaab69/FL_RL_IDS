"""Loading, preprocessing, splitting and partitioning of the ACI-IoT-2023 data.

Steps (thesis Table 4-3, with the choices recorded in the README):
  1. read the CSV, drop the label and excluded columns, coerce to numbers, impute medians;
  2. optional stratified subsample (for quick runs);
  3. encode labels (binary: benign=0 / attack=1; multiclass: benign=0, then each attack);
  4. optional zero-day holdout: the held-out class is removed from training and kept for testing;
  5. stratified train/test split, standardisation fitted on the training rows;
  6. optional SMOTE on the training rows (applied before partitioning, as in the thesis);
  7. partition the training rows across clients: iid, label_skew (thesis non-IID) or dirichlet.
"""
from __future__ import annotations

import hashlib
import os
import warnings
from dataclasses import dataclass

import numpy as np

from .config import DataConfig

PKG_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.environ.get("FL_IDS_CACHE", os.path.join(os.path.dirname(PKG_DIR), "cache"))


@dataclass
class Dataset:
    X_train: np.ndarray       # standardised float32 features
    y_train: np.ndarray       # class ids (binary: 0 benign, 1 attack)
    X_test: np.ndarray
    y_test: np.ndarray
    test_raw: np.ndarray      # original label strings for the test rows
    class_names: list         # index 0 is Benign
    task: str

    @property
    def n_features(self) -> int:
        return self.X_train.shape[1]


def _raw_cache_path(cfg: DataConfig) -> str:
    st = os.stat(cfg.csv_path)
    blob = f"{os.path.abspath(cfg.csv_path)}|{st.st_size}|{st.st_mtime_ns}|{cfg.label_col}|{cfg.drop_cols}"
    return os.path.join(CACHE_DIR, "raw_" + hashlib.sha1(blob.encode()).hexdigest()[:16] + ".npz")


def load_raw(cfg: DataConfig):
    """Return (features float32 [n, d], raw label strings [n]) for the whole CSV, cached on disk."""
    path = _raw_cache_path(cfg)
    if os.path.exists(path):
        with np.load(path, allow_pickle=False) as z:
            return z["X"], z["labels"]

    import pandas as pd
    df = pd.read_csv(cfg.csv_path, low_memory=False)
    labels = df[cfg.label_col].astype(str).str.strip().to_numpy()
    feats = df.drop(columns=[cfg.label_col, *cfg.drop_cols], errors="ignore")
    for col in feats.columns:
        if feats[col].dtype == object:
            feats[col] = pd.factorize(feats[col])[0]          # ordinal codes for nominal columns
    X = feats.apply(pd.to_numeric, errors="coerce").to_numpy(dtype=np.float64)
    X[~np.isfinite(X)] = np.nan
    med = np.nanmedian(X, axis=0) if len(X) else np.zeros(X.shape[1])
    med = np.where(np.isfinite(med), med, 0.0)
    rows, cols = np.where(np.isnan(X))
    X[rows, cols] = med[cols]
    X = X.astype(np.float32)

    labels = labels.astype(str)
    os.makedirs(CACHE_DIR, exist_ok=True)
    np.savez(path, X=X, labels=labels)
    return X, labels


def stratified_indices(labels: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    """Indices of a stratified subsample of about n rows (every class keeps at least one row)."""
    classes, inverse = np.unique(labels, return_inverse=True)
    picks = []
    for c in range(len(classes)):
        pos = np.flatnonzero(inverse == c)
        k = min(len(pos), max(1, int(round(n * len(pos) / len(labels)))))
        picks.append(rng.choice(pos, size=k, replace=False))
    return np.sort(np.concatenate(picks))


def encode_labels(raw: np.ndarray, task: str):
    """Map raw label strings to class ids. Benign is always class 0."""
    raw = np.asarray(raw, dtype=str)
    is_benign = np.char.lower(raw) == "benign"
    if task == "binary":
        return (~is_benign).astype(np.int64), ["Benign", "Attack"]
    if task != "multiclass":
        raise ValueError(f"unknown task {task!r}")
    attack_names = sorted(set(raw[~is_benign].tolist()))
    y = np.zeros(len(raw), dtype=np.int64)
    for i, name in enumerate(attack_names, start=1):
        y[raw == name] = i
    return y, ["Benign"] + attack_names


def stratified_split(y: np.ndarray, test_fraction: float, rng: np.random.Generator):
    """Return (train_positions, test_positions) into y, stratified by class."""
    train, test = [], []
    for c in np.unique(y):
        pos = rng.permutation(np.flatnonzero(y == c))
        cut = int(round(len(pos) * (1.0 - test_fraction)))
        if len(pos) >= 2:
            cut = min(max(cut, 1), len(pos) - 1)
        train.append(pos[:cut])
        test.append(pos[cut:])
    return np.sort(np.concatenate(train)), np.sort(np.concatenate(test))


def oversample(X: np.ndarray, y: np.ndarray, cap: int, seed: int):
    """SMOTE: classes with fewer than min(cap, largest class) rows are oversampled up to that size."""
    counts = np.bincount(y)
    target_size = min(cap, int(counts.max()))
    strategy = {c: target_size for c in range(len(counts)) if 2 <= counts[c] < target_size}
    if not strategy:
        return X, y
    from imblearn.over_sampling import SMOTE

    k = max(1, min(5, min(counts[c] for c in strategy) - 1))
    try:
        Xr, yr = SMOTE(sampling_strategy=strategy, k_neighbors=k, random_state=seed).fit_resample(X, y)
    except ValueError as exc:  # e.g. a class too small for the neighbour count
        warnings.warn(f"SMOTE skipped: {exc}")
        return X, y
    return Xr.astype(np.float32), yr


def build_dataset(cfg: DataConfig) -> Dataset:
    rng = np.random.default_rng(cfg.seed)
    X_all, raw = load_raw(cfg)
    if cfg.max_rows and cfg.max_rows < len(raw):
        keep = stratified_indices(raw, cfg.max_rows, rng)
        X_all, raw = X_all[keep], raw[keep]

    y_all, class_names = encode_labels(raw, cfg.task)
    if cfg.holdout_class is not None:
        hold = raw == cfg.holdout_class
        if not hold.any():
            raise ValueError(f"holdout class {cfg.holdout_class!r} not found in the data")
    else:
        hold = np.zeros(len(raw), dtype=bool)

    pool = np.flatnonzero(~hold)
    tr_rel, te_rel = stratified_split(y_all[pool], cfg.test_fraction, rng)
    tr = pool[tr_rel]
    te = np.concatenate([pool[te_rel], np.flatnonzero(hold)])

    mu = X_all[tr].mean(axis=0)
    sd = X_all[tr].std(axis=0)
    sd[sd == 0] = 1.0
    X_train = ((X_all[tr] - mu) / sd).astype(np.float32)
    y_train = y_all[tr]
    if cfg.smote:
        X_train, y_train = oversample(X_train, y_train, cfg.smote_cap, cfg.seed)
    X_test = ((X_all[te] - mu) / sd).astype(np.float32)

    return Dataset(
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_all[te],
        test_raw=raw[te],
        class_names=class_names,
        task=cfg.task,
    )


def partition(y: np.ndarray, n_clients: int, scheme: str, alpha: float,
              rng: np.random.Generator) -> list:
    """Split row indices of y across clients."""
    idx = np.arange(len(y))
    if scheme == "iid":
        return list(np.array_split(rng.permutation(idx), n_clients))
    if scheme == "label_skew":                      # thesis non-IID: contiguous blocks of sorted labels
        order = np.lexsort((rng.random(len(y)), y))
        return list(np.array_split(order, n_clients))
    if scheme == "dirichlet":
        parts = [[] for _ in range(n_clients)]
        for c in np.unique(y):
            pos = rng.permutation(np.flatnonzero(y == c))
            props = rng.dirichlet(alpha * np.ones(n_clients))
            cuts = (np.cumsum(props) * len(pos)).astype(int)[:-1]
            for i, chunk in enumerate(np.split(pos, cuts)):
                parts[i].append(chunk)
        return [np.sort(np.concatenate(p)) if p else np.array([], dtype=np.int64) for p in parts]
    raise ValueError(f"unknown partition {scheme!r}")
