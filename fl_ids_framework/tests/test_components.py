"""Unit tests for aggregators, privacy, defences, attacks and metrics (no dataset needed)."""
import math

import numpy as np
import pytest

from fl_ids import aggregators as A
from fl_ids import attacks, defenses, metrics, privacy
from fl_ids.config import AttackConfig, FedConfig, PrivacyConfig


# ---------------------------------------------------------------- aggregators

def test_fedavg_uses_weights():
    out, _ = A.fedavg(np.array([[0.0, 0.0], [4.0, 8.0]]), [3.0, 1.0])
    assert np.allclose(out, [1.0, 2.0])


def test_geometric_median_resists_outliers():
    rng = np.random.default_rng(0)
    base = rng.normal(size=40)
    honest = base + rng.normal(scale=0.01, size=(6, 40))
    poisoned = np.tile(base + 100.0, (4, 1))
    U = np.vstack([honest, poisoned])
    gm, _ = A.geometric_median(U)
    mean = U.mean(axis=0)
    assert np.linalg.norm(gm - base) < 0.5
    assert np.linalg.norm(mean - base) > 10 * np.linalg.norm(gm - base)


def test_geometric_median_satisfies_first_order_condition():
    rng = np.random.default_rng(1)
    U = rng.normal(size=(9, 20))
    m, _ = A.geometric_median(U)
    diffs = U - m
    norms = np.linalg.norm(diffs, axis=1)
    residual = np.linalg.norm(np.sum(diffs / norms[:, None], axis=0)) / len(U)
    assert residual < 5e-3


def test_geometric_median_weights_change_result():
    U = np.array([[0.0], [1.0], [10.0]])
    a, _ = A.geometric_median(U, [1, 1, 1])
    b, _ = A.geometric_median(U, [0.01, 0.01, 10])
    assert abs(a[0] - b[0]) > 0.5


def test_krum_selects_an_inlier():
    rng = np.random.default_rng(2)
    U = np.vstack([rng.normal(size=(7, 10)), 50 + rng.normal(size=(3, 10))])
    _, info = A.krum(U, f=3)
    assert info["selected"][0] < 7


def test_multi_krum_excludes_outliers():
    rng = np.random.default_rng(3)
    U = np.vstack([rng.normal(size=(7, 10)), 50 + rng.normal(size=(3, 10))])
    vec, info = A.krum(U, f=3, multi=True)
    assert all(i < 7 for i in info["selected"])
    assert np.linalg.norm(vec) < 5


def test_trimmed_mean_removes_extremes():
    U = np.array([[0.0], [1.0], [2.0], [3.0], [1000.0]])
    vec, _ = A.trimmed_mean(U, ratio=0.2)
    assert np.isclose(vec[0], 2.0)


def test_aggregate_dispatch_reports_time_and_rejects_unknown():
    U = np.ones((4, 3))
    vec, info = A.aggregate("median", U)
    assert np.allclose(vec, 1.0) and info["seconds"] >= 0
    with pytest.raises(ValueError):
        A.aggregate("nope", U)


# ------------------------------------------------------------------- privacy

def test_gaussian_sigma_matches_formula():
    sigma = privacy.gaussian_sigma(1.0, 1e-5, 1.0)
    assert math.isclose(sigma, math.sqrt(2 * math.log(1.25 / 1e-5)), rel_tol=1e-12)
    assert 4.84 < sigma < 4.85


def test_clip_l2_bounds_norm():
    v = np.array([3.0, 4.0])
    assert np.isclose(np.linalg.norm(privacy.clip_l2(v, 1.0)), 1.0)
    assert np.allclose(privacy.clip_l2(v, 10.0), v)


def test_protect_update_target_noise_scale():
    cfg = PrivacyConfig(dp=True, epsilon=1.0, delta=1e-5, clip_norm=0.1, target="update")
    rng = np.random.default_rng(0)
    g = np.zeros(20000)
    local = np.full(20000, 0.001)
    out, sigma = privacy.protect(local, g, cfg, rng)
    assert np.isclose(sigma, privacy.gaussian_sigma(1.0, 1e-5, 0.1))
    assert abs(np.std(out - g) - sigma) / sigma < 0.05


def test_protect_rejects_unknown_target():
    with pytest.raises(ValueError):
        privacy.protect(np.zeros(3), np.zeros(3), PrivacyConfig(target="nope"), np.random.default_rng(0))


# ------------------------------------------------------------------ defences

def test_quality_gate_accuracy_and_f1():
    cfg = FedConfig(gate="accuracy", gate_threshold=0.85)
    assert defenses.quality_passes({"accuracy": 0.9, "f1": 0.0}, cfg)
    assert not defenses.quality_passes({"accuracy": 0.8, "f1": 1.0}, cfg)
    cfg = FedConfig(gate="f1", gate_threshold=0.3)
    assert defenses.quality_passes({"accuracy": 0.0, "f1": 0.5}, cfg)
    assert defenses.quality_passes({"accuracy": 0.0, "f1": 0.0}, FedConfig(gate="none"))


def test_zscore_filter_flags_the_outlier_client():
    # With population standard deviation the largest possible |Z| is (n-1)/sqrt(n):
    # 2.47 for 8 clients, so the thesis rule |Z| > 3 needs at least 11 clients to fire.
    rng = np.random.default_rng(0)
    V = rng.normal(size=(20, 200))
    V[19] += 50.0
    flags = defenses.anomaly_flags(V, FedConfig(anomaly_filter="zscore", anomaly_limit=3.0,
                                                anomaly_fraction=0.05))
    assert flags[19] and not flags[:19].any()


def test_zscore_rule_cannot_fire_with_eight_clients():
    rng = np.random.default_rng(0)
    V = rng.normal(size=(8, 200))
    V[7] += 50.0
    flags = defenses.anomaly_flags(V, FedConfig(anomaly_filter="zscore", anomaly_limit=3.0,
                                                anomaly_fraction=0.05))
    assert not flags.any()


def test_iqr_filter_flags_the_outlier_client():
    rng = np.random.default_rng(1)
    V = rng.normal(size=(8, 200))
    V[0] += 50.0
    flags = defenses.anomaly_flags(V, FedConfig(anomaly_filter="iqr", anomaly_fraction=0.05))
    assert flags[0]


def test_exclusion_after_patience_and_readmission():
    t = defenses.ExclusionTracker(patience=3)
    for _ in range(2):
        t.record(5, False)
    assert not t.is_suspended(5)
    t.record(5, False)
    assert t.is_suspended(5)
    t.record(5, True)
    assert not t.is_suspended(5)


def test_client_weights_modes():
    assert np.allclose(defenses.client_weights("none", [0.1, 0.9], [0.1, 0.9], [1, 1]), [1, 1])
    assert np.allclose(defenses.client_weights("f1", [0.2, 0.6], [0, 0], [1, 1]), [0.2, 0.6])
    mm = defenses.client_weights("f1_minmax", [0.2, 0.6], [0, 0], [1, 1])
    assert np.allclose(mm, [0.0, 1.0])
    with pytest.raises(ValueError):
        defenses.client_weights("bogus", [1], [1], [1])


# ------------------------------------------------------------------- attacks

def test_flip_labels_binary_fraction():
    y = np.zeros(1000, dtype=np.int64)
    out = attacks.flip_labels(y, 0.5, 2, np.random.default_rng(0))
    assert (out != y).sum() == 500


def test_flip_labels_multiclass_never_keeps_class():
    y = np.arange(300) % 4
    out = attacks.flip_labels(y, 1.0, 4, np.random.default_rng(0))
    assert (out != y).all()


def test_manipulate_update_kinds():
    rng = np.random.default_rng(0)
    g = np.zeros(5)
    local = np.ones(5)
    assert np.allclose(attacks.manipulate_update(local, g, AttackConfig(kind="sign_flip"), rng), -1)
    assert np.allclose(attacks.manipulate_update(local, g, AttackConfig(kind="scaling", scale_factor=10), rng), 10)
    noisy = attacks.manipulate_update(local, g, AttackConfig(kind="model_noise", noise_std=10), rng)
    assert noisy.std() > 1


def test_select_malicious_count():
    assert len(attacks.select_malicious(10, 4, np.random.default_rng(0))) == 4
    assert attacks.select_malicious(10, 0, np.random.default_rng(0)) == set()


# ------------------------------------------------------------------- metrics

def test_detection_metrics_known_confusion():
    m = metrics.detection_metrics([1, 1, 0, 0, 1], [1, 0, 0, 1, 1])
    assert (m["tp"], m["fn"], m["fp"], m["tn"]) == (2, 1, 1, 1)
    assert np.isclose(m["precision"], 2 / 3) and np.isclose(m["recall"], 2 / 3)
    assert np.isclose(m["f1"], 2 / 3) and np.isclose(m["fpr"], 0.5)


def test_per_class_detection_skips_benign():
    raw = np.array(["Benign", "Port Scan", "Port Scan", "ICMP Flood"])
    pred = np.array([False, True, False, True])
    out = metrics.per_class_detection(raw, pred)
    assert set(out) == {"Port Scan", "ICMP Flood"}
    assert out["Port Scan"] == 0.5


def test_membership_auc_chance_and_perfect():
    y = [1, 1, 0, 0]
    same = metrics.membership_auc([0.9, 0.9, 0.1, 0.1], y, [0.9, 0.9, 0.1, 0.1], y)
    assert same == pytest.approx(0.5)
    perfect = metrics.membership_auc([0.9, 0.9, 0.1, 0.1], y, [0.5, 0.5, 0.5, 0.5], y)
    assert perfect == pytest.approx(1.0)
