"""Evaluation metrics: detection metrics (F1, FPR, FNR), per-class detection rates, membership-inference AUC."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import f1_score, roc_auc_score


def detection_metrics(y_true, pred_attack) -> dict:
    """Binary detection metrics. y_true and pred_attack are booleans or 0/1 (1 = attack)."""
    t = np.asarray(y_true).astype(bool)
    p = np.asarray(pred_attack).astype(bool)
    tp = int(np.sum(t & p))
    tn = int(np.sum(~t & ~p))
    fp = int(np.sum(~t & p))
    fn = int(np.sum(t & ~p))
    n = tp + tn + fp + fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "accuracy": (tp + tn) / n if n else 0.0,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fp / (fp + tn) if fp + tn else 0.0,
        "fnr": fn / (fn + tp) if fn + tp else 0.0,
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
    }


def per_class_detection(raw_true, pred_attack) -> dict:
    """Share of each attack class that is flagged as an attack (its detection rate)."""
    raw_true = np.asarray(raw_true).astype(str)
    p = np.asarray(pred_attack).astype(bool)
    out = {}
    for name in np.unique(raw_true):
        if name.lower() == "benign":
            continue
        out[name] = float(np.mean(p[raw_true == name]))
    return out


def multiclass_scores(y_true, y_pred) -> dict:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return {
        "accuracy": float(np.mean(y_true == y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
    }


def membership_auc(p_attack_in, y_in, p_attack_out, y_out) -> float:
    """AUC of a confidence-based membership-inference attack.

    The attacker scores a sample by the model's confidence in its true label. An AUC of 0.5
    means members (training rows) and non-members (test rows) look the same to the model.
    """
    p_in = np.asarray(p_attack_in, dtype=np.float64)
    p_out = np.asarray(p_attack_out, dtype=np.float64)
    s_in = np.where(np.asarray(y_in) == 1, p_in, 1.0 - p_in)
    s_out = np.where(np.asarray(y_out) == 1, p_out, 1.0 - p_out)
    scores = np.concatenate([s_in, s_out])
    labels = np.concatenate([np.ones(len(s_in)), np.zeros(len(s_out))])
    return float(roc_auc_score(labels, scores))
