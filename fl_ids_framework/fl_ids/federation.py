"""Federated PPO simulator (thesis Algorithm 1), centralised baselines and the aggregation benchmark.

Per round (thesis Sec. 3-4-3, phases 1-4):
  1. each client receives the global policy and blends it with its own: (1-beta)*local + beta*global;
  2. local PPO training on its private samples (malicious clients may flip labels or manipulate
     what they send);
  3. each client reports the validation metrics of the vector it sends, then optionally applies
     differential privacy to that vector;
  4. the server applies the quality gate, the anomaly filter and the exclusion rule, weights the
     accepted clients, aggregates, and evaluates the new global policy on the test set.
"""
from __future__ import annotations

import time

import numpy as np
import torch
from torch.optim import Adam

from . import agents, aggregators, attacks, defenses, metrics, privacy
from .config import ExperimentConfig
from .data import Dataset, partition

MIA_SAMPLE = 2000
MODEL_ATTACKS = ("model_noise", "sign_flip", "scaling")


def _evaluate(ds: Dataset, pred_attack: np.ndarray) -> dict:
    m = metrics.detection_metrics(ds.y_test, pred_attack)
    m["per_class_detection"] = metrics.per_class_detection(ds.test_raw, pred_attack)
    return m


def _mia_indices(ds: Dataset, rng: np.random.Generator):
    mi = rng.choice(len(ds.X_train), size=min(MIA_SAMPLE, len(ds.X_train)), replace=False)
    mo = rng.choice(len(ds.X_test), size=min(MIA_SAMPLE, len(ds.X_test)), replace=False)
    return mi, mo


def run_federated(cfg: ExperimentConfig, ds: Dataset, log=print) -> dict:
    fed, agent, atk, dp = cfg.fed, cfg.agent, cfg.attack, cfg.privacy
    rng = np.random.default_rng(cfg.seed)
    torch.manual_seed(cfg.seed)
    n_cls = 2 if ds.task == "binary" else len(ds.class_names)
    n_act = agents.n_actions(agent)
    inc = fed.share_critic
    bin_train = (ds.y_train != 0).astype(np.int64)     # reward uses binary attack labels

    parts = partition(ds.y_train, fed.n_clients, cfg.data.partition, cfg.data.dirichlet_alpha, rng)
    malicious = attacks.select_malicious(fed.n_clients, atk.n_malicious, rng) if atk.kind != "none" else set()

    init = agents.ActorCritic(ds.n_features, n_act, agent.hidden)
    gvec = agents.get_vector(init, inc)
    g_model = agents.ActorCritic(ds.n_features, n_act, agent.hidden)
    scratch = agents.ActorCritic(ds.n_features, n_act, agent.hidden)

    clients = []
    for cid, idx in enumerate(parts):
        idx = rng.permutation(idx)
        n_val = max(1, int(round(len(idx) * cfg.data.validation_fraction)))
        v_idx, t_idx = idx[:n_val], idx[n_val:]
        if len(t_idx) == 0:
            raise ValueError(f"client {cid} has no training rows; use fewer clients or more data")
        X, y = ds.X_train[t_idx], ds.y_train[t_idx]
        is_mal = cid in malicious
        if is_mal and atk.kind == "label_flip":
            y = attacks.flip_labels(y, atk.flip_fraction, n_cls, rng)
        model = agents.ActorCritic(ds.n_features, n_act, agent.hidden)
        agents.set_vector(model, gvec, inc)
        clients.append({
            "cid": cid,
            "model": model,
            "opt": Adam(model.parameters(), lr=agent.lr),
            "env": agents.SampleEnv(X, (y != 0).astype(np.int64), agent,
                                    np.random.default_rng(cfg.seed + 1000 + cid)),
            "Xv": ds.X_train[v_idx],
            "yv": ds.y_train[v_idx],
            "malicious": is_mal,
            "n": int(len(X)),
        })

    mi, mo = _mia_indices(ds, rng)
    truth_in = bin_train[mi]
    truth_out = (ds.y_test[mo] != 0).astype(np.int64)
    tracker = defenses.ExclusionTracker(fed.exclusion_patience)
    history, sigma = [], None
    n = len(clients)

    for rnd in range(1, fed.rounds + 1):
        t_round = time.perf_counter()
        sent, reports = [], []
        for c in clients:
            local = agents.get_vector(c["model"], inc)
            agents.set_vector(c["model"], (1.0 - fed.blend_beta) * local + fed.blend_beta * gvec, inc)
            agents.ppo_train(c["model"], c["opt"], c["env"], agent, fed.local_steps)
            honest = agents.get_vector(c["model"], inc)
            vec = honest
            if c["malicious"] and atk.kind in MODEL_ATTACKS:
                vec = attacks.manipulate_update(honest, gvec, atk, rng)
            agents.set_vector(scratch, vec, inc)
            pred = agents.predict_actions(scratch, c["Xv"]) != 0
            reports.append(metrics.detection_metrics(c["yv"] != 0, pred))
            if dp.dp:
                vec, sigma = privacy.protect(vec, gvec, dp, rng)
            sent.append(vec)

        V = np.stack(sent)
        gate_ok = np.array([defenses.quality_passes(r, fed) for r in reports])
        flagged = np.zeros(n, dtype=bool)
        gate_idx = np.flatnonzero(gate_ok)
        if len(gate_idx) >= 3:
            flagged[gate_idx] = defenses.anomaly_flags(V[gate_idx], fed)
        for i, c in enumerate(clients):
            tracker.record(c["cid"], bool(gate_ok[i] and not flagged[i]))
        included = [i for i, c in enumerate(clients)
                    if gate_ok[i] and not flagged[i] and not tracker.is_suspended(c["cid"])]

        if included:
            w = defenses.client_weights(
                fed.weighting,
                [reports[i]["f1"] for i in included],
                [reports[i]["accuracy"] for i in included],
                [clients[i]["n"] for i in included],
            )
            f = fed.krum_f if fed.krum_f is not None else atk.n_malicious
            gvec, agg_info = aggregators.aggregate(fed.aggregator, V[included], w, f=f,
                                                   trim_ratio=fed.trim_ratio)
        else:
            agg_info = {"skipped": True, "seconds": 0.0}

        agents.set_vector(g_model, gvec, inc)
        test = _evaluate(ds, agents.predict_actions(g_model, ds.X_test) != 0)
        p_in = agents.attack_probability(g_model, ds.X_train[mi])
        p_out = agents.attack_probability(g_model, ds.X_test[mo])
        test["mia_auc"] = metrics.membership_auc(p_in, truth_in, p_out, truth_out)

        history.append({
            "round": rnd,
            "included": [clients[i]["cid"] for i in included],
            "gate_rejected": [c["cid"] for i, c in enumerate(clients) if not gate_ok[i]],
            "anomaly_flagged": [c["cid"] for i, c in enumerate(clients) if flagged[i]],
            "suspended": sorted(tracker.suspended),
            "client_reports": [
                {"cid": c["cid"], "malicious": c["malicious"],
                 "accuracy": r["accuracy"], "f1": r["f1"]}
                for c, r in zip(clients, reports)
            ],
            "aggregation": agg_info,
            "test": test,
            "round_seconds": time.perf_counter() - t_round,
        })
        log(f"  round {rnd:2d}: included {len(included):2d}/{n}  F1={test['f1']:.4f}  "
            f"FPR={test['fpr']:.4f}  MIA-AUC={test['mia_auc']:.3f}  agg={agg_info.get('seconds', 0):.3f}s")

    return {
        "history": history,
        "final": history[-1]["test"],
        "malicious": sorted(malicious),
        "dp_sigma": sigma,
        "n_train": int(len(ds.y_train)),
    }


def _fit_baseline(name: str, X: np.ndarray, y: np.ndarray, seed: int):
    """Fit a classical classifier once. Returns (fitted model, class ids, column of the benign class)."""
    if name == "rf":
        from sklearn.ensemble import RandomForestClassifier
        clf = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=seed)
    elif name == "dt":
        from sklearn.tree import DecisionTreeClassifier
        clf = DecisionTreeClassifier(random_state=seed)
    elif name == "xgb":
        from xgboost import XGBClassifier
        clf = XGBClassifier(n_estimators=200, max_depth=8, tree_method="hist", random_state=seed, n_jobs=-1)
    elif name == "mlp":
        from sklearn.neural_network import MLPClassifier
        clf = MLPClassifier(hidden_layer_sizes=(256, 128, 64), max_iter=30, early_stopping=True,
                            random_state=seed)
    else:
        raise ValueError(f"unknown baseline {name!r}")
    classes, inv = np.unique(y, return_inverse=True)
    clf.fit(X, inv)
    benign = np.flatnonzero(classes == 0)
    return clf, classes, (int(benign[0]) if len(benign) else None)


def _baseline_scores(fitted, Xq: np.ndarray):
    clf, classes, benign_col = fitted
    pred = classes[np.asarray(clf.predict(Xq)).astype(int)]
    if benign_col is None:
        p_attack = np.ones(len(Xq))
    else:
        p_attack = 1.0 - clf.predict_proba(Xq)[:, benign_col]
    return pred, p_attack


def run_centralized(cfg: ExperimentConfig, ds: Dataset, log=print) -> dict:
    rng = np.random.default_rng(cfg.seed)
    torch.manual_seed(cfg.seed)
    total_steps = cfg.fed.rounds * cfg.fed.local_steps
    n_act = agents.n_actions(cfg.agent)
    mi, mo = _mia_indices(ds, rng)
    truth_in = (ds.y_train[mi] != 0).astype(np.int64)
    truth_out = (ds.y_test[mo] != 0).astype(np.int64)
    bin_train = (ds.y_train != 0).astype(np.int64)

    if cfg.model == "ppo":
        model = agents.ActorCritic(ds.n_features, n_act, cfg.agent.hidden)
        opt = Adam(model.parameters(), lr=cfg.agent.lr)
        env = agents.SampleEnv(ds.X_train, bin_train, cfg.agent, np.random.default_rng(cfg.seed + 1))
        agents.ppo_train(model, opt, env, cfg.agent, total_steps)
        pred = agents.predict_actions(model, ds.X_test) != 0
        p_in = agents.attack_probability(model, ds.X_train[mi])
        p_out = agents.attack_probability(model, ds.X_test[mo])
    elif cfg.model == "dqn":
        q = agents.QNet(ds.n_features, n_act, cfg.agent.hidden)
        target = agents.QNet(ds.n_features, n_act, cfg.agent.hidden)
        target.load_state_dict(q.state_dict())
        opt = Adam(q.parameters(), lr=1e-3)
        env = agents.SampleEnv(ds.X_train, bin_train, cfg.agent, np.random.default_rng(cfg.seed + 1))
        agents.dqn_train(q, target, opt, env, cfg.agent, total_steps, rng, n_act)
        pred = agents.q_predict_actions(q, ds.X_test) != 0
        p_in = agents.q_attack_probability(q, ds.X_train[mi])
        p_out = agents.q_attack_probability(q, ds.X_test[mo])
    elif cfg.model in ("rf", "dt", "xgb", "mlp"):
        fitted = _fit_baseline(cfg.model, ds.X_train, ds.y_train, cfg.seed)
        cls_pred, p_out_all = _baseline_scores(fitted, ds.X_test)
        pred = cls_pred != 0
        _, p_in = _baseline_scores(fitted, ds.X_train[mi])
        p_out = p_out_all[mo]
    else:
        raise ValueError(f"unknown centralised model {cfg.model!r}")

    final = _evaluate(ds, pred)
    final["mia_auc"] = metrics.membership_auc(p_in, truth_in, p_out, truth_out)
    log(f"  {cfg.model}: F1={final['f1']:.4f}  FPR={final['fpr']:.4f}  MIA-AUC={final['mia_auc']:.3f}")
    return {"final": final, "model": cfg.model, "budget_steps": total_steps}


def run_aggregation_bench(cfg: ExperimentConfig, log=print) -> dict:
    b = cfg.bench or {}
    ns = b.get("n_clients", [5, 10, 50, 100])
    ps = b.get("n_params", [23330])
    reps = int(b.get("repeats", 3))
    rng = np.random.default_rng(cfg.seed)
    rows = []
    for p in ps:
        for n in ns:
            U = rng.normal(size=(n, p))
            f = max(0, n // 10)
            for name in aggregators.AGGREGATORS:
                times = [aggregators.aggregate(name, U, None, f=f)[1]["seconds"] for _ in range(reps)]
                rows.append({"n_clients": n, "n_params": p, "aggregator": name,
                             "median_seconds": float(np.median(times))})
            log(f"  params={p} clients={n} done")
    return {"rows": rows}
