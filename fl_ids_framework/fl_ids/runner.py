"""Runs experiment configurations, caches each result as JSON, and loads them back for reports."""
from __future__ import annotations

import glob
import json
import os
import re
import time
import traceback

import numpy as np

from . import data as data_mod
from .config import ExperimentConfig
from .federation import run_aggregation_bench, run_centralized, run_federated

FRAMEWORK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.environ.get("FL_IDS_RESULTS", os.path.join(FRAMEWORK_DIR, "results"))

_DATASET = {"key": None, "ds": None}   # keeps the last dataset in memory between runs


def _json_default(o):
    if isinstance(o, np.generic):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (set, tuple)):
        return list(o)
    return str(o)


def result_path(cfg: ExperimentConfig) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.+-]+", "_", cfg.name)
    return os.path.join(RESULTS_DIR, f"{safe}__{cfg.key()}.json")


def _dataset_for(cfg: ExperimentConfig):
    key = json.dumps(cfg.data.__dict__, sort_keys=True, default=str)
    if _DATASET["key"] != key:
        _DATASET["ds"] = data_mod.build_dataset(cfg.data)
        _DATASET["key"] = key
    return _DATASET["ds"]


def run_one(cfg: ExperimentConfig, force: bool = False, log=print) -> dict:
    """Run one configuration, or return its cached record."""
    path = result_path(cfg)
    if os.path.exists(path) and not force:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)

    t0 = time.time()
    if cfg.kind == "aggregation_bench":
        result = run_aggregation_bench(cfg, log)
    elif cfg.kind == "federated":
        result = run_federated(cfg, _dataset_for(cfg), log)
    elif cfg.kind == "centralized":
        result = run_centralized(cfg, _dataset_for(cfg), log)
    else:
        raise ValueError(f"unknown kind {cfg.kind!r}")

    record = {
        "name": cfg.name,
        "config": cfg.to_dict(),
        "result": result,
        "seconds": round(time.time() - t0, 2),
        "finished": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, default=_json_default, indent=1)
    return record


def run_configs(configs, force: bool = False, only: str | None = None, log=print) -> list:
    """Run a list of configurations. A failing run is recorded and the others continue."""
    out = []
    for cfg in configs:
        if only and not re.search(only, cfg.name):
            continue
        log(f"[run] {cfg.name}")
        try:
            rec = run_one(cfg, force=force, log=log)
        except Exception as exc:  # recorded, not hidden
            rec = {"name": cfg.name, "error": f"{type(exc).__name__}: {exc}",
                   "traceback": traceback.format_exc()}
            log(f"  FAILED: {rec['error']}")
        out.append(rec)
    return out


def load_results() -> dict:
    """All cached records keyed by configuration name (the latest file wins)."""
    records = {}
    for path in sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json"))):
        with open(path, encoding="utf-8") as fh:
            rec = json.load(fh)
        if "name" in rec and "error" not in rec:
            records[rec["name"]] = rec
    return records
