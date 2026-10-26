"""Pipeline tests: reward, PPO learning, preprocessing, partitioning and small end-to-end runs."""
import numpy as np
import pytest
import torch

from fl_ids import agents, data
from fl_ids.config import AgentConfig, DataConfig, ExperimentConfig
from fl_ids.data import Dataset
from fl_ids.federation import run_centralized, run_federated


def synthetic(n=600, d=8, seed=0):
    rng = np.random.default_rng(seed)
    y = rng.integers(0, 2, n)
    X = (rng.normal(size=(n, d)) + 2.0 * y[:, None]).astype(np.float32)
    raw = np.where(y == 1, "Port Scan", "Benign")
    cut = int(0.75 * n)
    return Dataset(X[:cut], y[:cut], X[cut:], y[cut:], raw[cut:], ["Benign", "Attack"], "binary")


def small_cfg(name, **fed):
    cfg = ExperimentConfig(name=name)
    cfg.agent.rollout_steps = 128
    cfg.agent.episode_len = 64
    cfg.fed.n_clients = 3
    cfg.fed.rounds = 2
    cfg.fed.local_steps = 256
    for k, v in fed.items():
        setattr(cfg.fed, k, v)
    return cfg


# ---------------------------------------------------------------- reward

def test_binary_reward_table():
    cfg = AgentConfig(actions="binary", alpha=1.0, beta=1.0, gamma_resp=0.1, miss_penalty=0.0,
                      action_costs=(0.0, 1.0, 2.0, 1.0, 1.0))
    assert agents.reward(cfg, 1, 1) == pytest.approx(1.0 - 0.1 * 1.0)   # detection minus block cost
    assert agents.reward(cfg, 1, 0) == pytest.approx(-1.0 - 0.1 * 1.0)  # false alarm
    assert agents.reward(cfg, 0, 1) == pytest.approx(0.0)               # missed attack, no penalty
    assert agents.reward(cfg, 0, 0) == pytest.approx(0.0)


def test_five_action_reward_uses_action_cost():
    cfg = AgentConfig(actions="five", alpha=1.0, beta=1.0, gamma_resp=0.1)
    assert agents.reward(cfg, 2, 1) == pytest.approx(1.0 - 0.1 * 2.0)   # ISOLATE costs 2
    assert agents.n_actions(cfg) == 5


def test_vector_roundtrip_actor_only_and_with_critic():
    m = agents.ActorCritic(8, 2, (16, 8))
    v = agents.get_vector(m, include_critic=False)
    v_all = agents.get_vector(m, include_critic=True)
    assert len(v_all) > len(v)
    agents.set_vector(m, v + 1.0, include_critic=False)
    assert np.allclose(agents.get_vector(m, include_critic=False), v + 1.0, atol=1e-6)


# ------------------------------------------------------------- learning

def test_ppo_learns_separable_data():
    ds = synthetic(n=800)
    cfg = AgentConfig(rollout_steps=512, episode_len=128, epochs=4)
    torch.manual_seed(0)
    model = agents.ActorCritic(ds.n_features, 2, cfg.hidden)
    opt = torch.optim.Adam(model.parameters(), lr=cfg.lr)
    env = agents.SampleEnv(ds.X_train, ds.y_train, cfg, np.random.default_rng(0))
    agents.ppo_train(model, opt, env, cfg, steps=8192)
    acc = np.mean((agents.predict_actions(model, ds.X_test) != 0) == (ds.y_test != 0))
    assert acc > 0.9


# ------------------------------------------------------------ preprocessing

def _write_csv(path, n=300):
    rng = np.random.default_rng(0)
    rows = ["Protocol,Flow Duration,Connection Type,Label"]
    for i in range(n):
        label = "Benign" if i % 3 else "Port Scan"
        rows.append(f"{i % 3},{rng.normal() + (label != 'Benign') * 3:.4f},x,{label}")
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def test_build_dataset_from_csv(tmp_path, monkeypatch):
    monkeypatch.setattr(data, "CACHE_DIR", str(tmp_path / "cache"))
    csv = tmp_path / "toy.csv"
    _write_csv(csv)
    cfg = DataConfig(csv_path=str(csv), smote=False, test_fraction=0.2)
    ds = data.build_dataset(cfg)
    assert ds.n_features == 2                       # Connection Type dropped, Label removed
    assert abs(ds.X_train.mean()) < 1e-5            # standardised on the training rows
    assert set(np.unique(ds.y_train)) <= {0, 1}
    assert len(ds.test_raw) == len(ds.y_test)


def test_zero_day_holdout_is_removed_from_training(tmp_path, monkeypatch):
    monkeypatch.setattr(data, "CACHE_DIR", str(tmp_path / "cache"))
    csv = tmp_path / "toy.csv"
    _write_csv(csv)
    cfg = DataConfig(csv_path=str(csv), smote=False, holdout_class="Port Scan")
    ds = data.build_dataset(cfg)
    assert (ds.test_raw == "Port Scan").any()
    assert ds.y_train.sum() == 0                    # no attack rows left in training


def test_label_skew_partition_gives_contiguous_blocks():
    rng = np.random.default_rng(0)
    y = np.repeat(np.arange(4), 50)
    parts = data.partition(y, 4, "label_skew", 0.5, rng)
    assert all(len(np.unique(y[p])) <= 2 for p in parts)
    assert sum(len(p) for p in parts) == len(y)


def test_iid_partition_covers_every_row_once():
    rng = np.random.default_rng(0)
    y = np.zeros(103, dtype=int)
    parts = data.partition(y, 5, "iid", 0.5, rng)
    allidx = np.sort(np.concatenate(parts))
    assert np.array_equal(allidx, np.arange(103))


def test_stratified_split_keeps_every_class_in_test():
    rng = np.random.default_rng(0)
    y = np.array([0] * 80 + [1] * 20)
    tr, te = data.stratified_split(y, 0.25, rng)
    assert set(np.unique(y[te])) == {0, 1}


# ------------------------------------------------------- end-to-end smoke

def test_federated_run_returns_history_and_metrics():
    ds = synthetic()
    cfg = small_cfg("t/fed")
    cfg.fed.aggregator, cfg.fed.weighting = "geometric_median", "f1"
    out = run_federated(cfg, ds, log=lambda *_: None)
    assert len(out["history"]) == 2
    final = out["final"]
    for key in ("f1", "fpr", "fnr", "mia_auc", "per_class_detection"):
        assert key in final


def test_federated_run_survives_model_poisoning_with_gate():
    ds = synthetic()
    cfg = small_cfg("t/attack", gate="f1", gate_threshold=0.3)
    cfg.attack.kind = "model_noise"
    cfg.attack.n_malicious = 1
    out = run_federated(cfg, ds, log=lambda *_: None)
    rejected = [cid for rec in out["history"] for cid in rec["gate_rejected"]]
    assert out["malicious"] and rejected                       # the poisoned client is gated out


def test_centralized_rf_and_ppo_run():
    ds = synthetic()
    cfg = small_cfg("t/rf", kind="centralized")
    cfg.model = "rf"
    out = run_centralized(cfg, ds, log=lambda *_: None)
    assert out["final"]["f1"] > 0.8
    cfg.model = "ppo"
    cfg.fed.rounds, cfg.fed.local_steps = 2, 512
    out = run_centralized(cfg, ds, log=lambda *_: None)
    assert "mia_auc" in out["final"]
