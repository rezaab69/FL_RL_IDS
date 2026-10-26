"""Budgets, thesis profiles and scenario suites.

Profiles say which algorithm settings to use:
  thesis_spec      Chapter 3 rules: lambda 0.95, c1 0.5, c2 0.01, blend beta 0.3, critic local,
                   accuracy gate 85%, Z-score filter, exclusion after 3 failures, F1 weighting.
  thesis_table44   Table 4-4 PPO values (gamma 0.01, lambda 0.1, clip 0.1, entropy 0.07, ...)
                   with the thesis_spec federation rules.
  legacy_backup16  what backup16's new2 script does: gamma 0.01, lambda 0.1, clip 0.2, no entropy,
                   F1 gate at 0.3, no blend, critic shared, no filter, no exclusion.
  plain_fedavg     classic federated averaging with no defence.
  framework_default  the framework's own defaults.

Budgets say how large the runs are. "full" is the thesis budget (whole dataset, 10 rounds,
20,000 PPO steps per client per round). Expect hours for the full grids.
"""
from __future__ import annotations

from .config import ExperimentConfig

BUDGETS = {
    "smoke": dict(max_rows=6000, rounds=2, local_steps=1024, rollout=512, clients=4),
    "quick": dict(max_rows=30000, rounds=3, local_steps=4096, rollout=1024, clients=10),
    "standard": dict(max_rows=200000, rounds=5, local_steps=8192, rollout=2048, clients=10),
    "full": dict(max_rows=None, rounds=10, local_steps=20000, rollout=2048, clients=10),
}

_THESIS_FED = dict(
    aggregator="geometric_median", weighting="f1", gate="accuracy", gate_threshold=0.85,
    anomaly_filter="zscore", exclusion_patience=3, blend_beta=0.3, share_critic=False,
)

PROFILES = {
    "framework_default": {"agent": {}, "fed": {}},
    "thesis_spec": {
        "agent": dict(gamma=0.99, gae_lambda=0.95, clip=0.2, ent_coef=0.01, vf_coef=0.5,
                      max_grad_norm=1.0, epochs=10, minibatch=64, lr=3e-4),
        "fed": dict(_THESIS_FED),
    },
    "thesis_table44": {
        "agent": dict(gamma=0.01, gae_lambda=0.1, clip=0.1, ent_coef=0.07, vf_coef=0.1,
                      max_grad_norm=0.7, epochs=10, minibatch=64, lr=3e-4),
        "fed": dict(_THESIS_FED),
    },
    "legacy_backup16": {
        "agent": dict(actions="binary", gamma=0.01, gae_lambda=0.1, clip=0.2, ent_coef=0.0,
                      vf_coef=0.5, max_grad_norm=0.5, epochs=10, minibatch=64, lr=3e-4),
        "fed": dict(aggregator="geometric_median", weighting="none", gate="f1", gate_threshold=0.3,
                    anomaly_filter="none", exclusion_patience=0, blend_beta=1.0, share_critic=True),
    },
    "plain_fedavg": {
        "agent": {},
        "fed": dict(aggregator="fedavg", weighting="none", gate="none", anomaly_filter="none",
                    exclusion_patience=0, blend_beta=1.0, share_critic=True),
    },
}

AGG_VARIANTS = [
    ("fedavg", "none"), ("fedavg", "f1"),
    ("geometric_median", "none"), ("geometric_median", "f1"),
    ("krum", "none"), ("multi_krum", "none"),
    ("trimmed_mean", "none"), ("median", "none"),
]

ZERO_DAY_CLASSES = [
    "Port Scan", "ICMP Flood", "Ping Sweep", "DNS Flood", "Vulnerability Scan", "OS Scan",
    "Slowloris", "SYN Flood", "Dictionary Attack", "UDP Flood", "ARP Spoofing",
]
ZERO_DAY_QUICK = ["Port Scan", "ICMP Flood", "Slowloris"]
BASELINE_MODELS = ["ppo", "dqn", "rf", "dt", "xgb", "mlp"]


def base(name: str, profile: str = "framework_default", budget: str = "quick",
         kind: str = "federated", seed: int = 42) -> ExperimentConfig:
    if budget not in BUDGETS:
        raise ValueError(f"unknown budget {budget!r}")
    if profile not in PROFILES:
        raise ValueError(f"unknown profile {profile!r}")
    b, p = BUDGETS[budget], PROFILES[profile]
    cfg = ExperimentConfig(name=name, kind=kind, seed=seed)
    cfg.data.max_rows = b["max_rows"]
    cfg.fed.rounds = b["rounds"]
    cfg.fed.local_steps = b["local_steps"]
    cfg.fed.n_clients = b["clients"]
    cfg.agent.rollout_steps = b["rollout"]
    for k, v in p["agent"].items():
        setattr(cfg.agent, k, v)
    for k, v in p["fed"].items():
        setattr(cfg.fed, k, v)
    return cfg


def _aggregator_only(cfg: ExperimentConfig) -> ExperimentConfig:
    """Isolates the aggregation rule: no gate, no filter, no exclusion, full replacement, critic shared."""
    cfg.fed.gate = "none"
    cfg.fed.anomaly_filter = "none"
    cfg.fed.exclusion_patience = 0
    cfg.fed.blend_beta = 1.0
    cfg.fed.share_critic = False
    cfg.data.partition = "iid"
    return cfg


def suite_smoke(budget):
    fed = _aggregator_only(base("smoke/federated", "framework_default", budget))
    fed.fed.weighting = "f1"
    bench = ExperimentConfig(name="smoke/bench", kind="aggregation_bench",
                             bench={"n_clients": [5, 10], "n_params": [2000], "repeats": 1})
    central = base("smoke/centralized_rf", "framework_default", budget, kind="centralized")
    central.model = "rf"
    return [fed, bench, central]


def suite_aggregators(budget):
    out = []
    for agg, w in AGG_VARIANTS:
        cfg = _aggregator_only(base(f"agg/clean/{agg}+{w}", "framework_default", budget))
        cfg.fed.aggregator, cfg.fed.weighting = agg, w
        out.append(cfg)
    return out


def suite_poisoning(budget):
    out = []
    for agg, w in AGG_VARIANTS:
        cfg = _aggregator_only(base(f"poison/clean/{agg}+{w}", "framework_default", budget))
        cfg.fed.aggregator, cfg.fed.weighting = agg, w
        out.append(cfg)
    for kind in ("label_flip", "model_noise"):
        for frac in (0.2, 0.4, 0.6):
            for agg, w in AGG_VARIANTS:
                cfg = _aggregator_only(base(f"poison/{kind}/{int(frac * 100)}/{agg}+{w}",
                                            "framework_default", budget))
                cfg.fed.aggregator, cfg.fed.weighting = agg, w
                cfg.attack.kind = kind
                cfg.attack.n_malicious = max(1, round(frac * cfg.fed.n_clients))
                out.append(cfg)
    return out


def suite_defenses(budget):
    combos = [
        ("none", "none", "none", 0),
        ("gate", "accuracy", "none", 0),
        ("gate+zscore", "accuracy", "zscore", 0),
        ("gate+zscore+exclusion", "accuracy", "zscore", 3),
    ]
    out = []
    for label, gate, anomaly, patience in combos:
        for attack in ("clean", "model_noise"):
            cfg = base(f"defense/{attack}/{label}", "thesis_spec", budget)
            cfg.data.partition = "iid"
            cfg.fed.gate, cfg.fed.anomaly_filter, cfg.fed.exclusion_patience = gate, anomaly, patience
            if attack == "model_noise":
                cfg.attack.kind = "model_noise"
                cfg.attack.n_malicious = max(1, round(0.4 * cfg.fed.n_clients))
            out.append(cfg)
    return out


def suite_dp(budget):
    variants = [
        ("nodp", None, None, None),
        ("update_eps8_C1", "update", 8.0, 1.0),
        ("update_eps1_C0.1", "update", 1.0, 0.1),
        ("update_eps1_C1", "update", 1.0, 1.0),
        ("parameters_eps1_literal", "parameters", 1.0, 1.0),
    ]
    out = []
    for label, target, eps, clip in variants:
        cfg = _aggregator_only(base(f"dp/{label}", "framework_default", budget))
        cfg.fed.aggregator, cfg.fed.weighting = "geometric_median", "f1"
        if target is not None:
            cfg.privacy.dp = True
            cfg.privacy.target = target
            cfg.privacy.epsilon = eps
            cfg.privacy.clip_norm = clip
        out.append(cfg)
    central = base("dp/centralized_ppo", "framework_default", budget, kind="centralized")
    central.model = "ppo"
    central.data.partition = "iid"
    out.append(central)
    return out


def suite_zero_day(budget):
    classes = ZERO_DAY_QUICK if budget in ("smoke", "quick") else ZERO_DAY_CLASSES
    out = []
    for cls in classes:
        for model in BASELINE_MODELS:
            cfg = base(f"zeroday/{cls}/{model}", "framework_default", budget, kind="centralized")
            cfg.model = model
            cfg.data.task = "binary"
            cfg.data.holdout_class = cls
            out.append(cfg)
    return out


def suite_baselines(budget):
    out = []
    for task in ("binary", "multiclass"):
        for model in BASELINE_MODELS:
            if task == "multiclass" and model in ("ppo", "dqn"):
                continue                      # RL agents are detectors; they are evaluated on binary tasks
            cfg = base(f"baseline/{task}/{model}", "framework_default", budget, kind="centralized")
            cfg.model = model
            cfg.data.task = task
            out.append(cfg)
    return out


def suite_profiles(budget):
    out = []
    for profile in ("thesis_spec", "thesis_table44", "legacy_backup16", "plain_fedavg"):
        clean = base(f"profile/{profile}/clean", profile, budget)
        clean.data.partition = "iid"
        attacked = base(f"profile/{profile}/model_noise60", profile, budget)
        attacked.data.partition = "iid"
        attacked.attack.kind = "model_noise"
        attacked.attack.n_malicious = max(1, round(0.6 * attacked.fed.n_clients))
        out += [clean, attacked]
    return out


def suite_scaling(budget):
    ps = [23330] if budget in ("smoke", "quick") else [5410, 23330]
    ns = [5, 10, 50, 100]
    return [ExperimentConfig(name="scaling/bench", kind="aggregation_bench",
                             bench={"n_clients": ns, "n_params": ps, "repeats": 3})]


SUITE_BUILDERS = {
    "smoke": suite_smoke,
    "aggregators": suite_aggregators,
    "poisoning": suite_poisoning,
    "defenses": suite_defenses,
    "dp": suite_dp,
    "zero_day": suite_zero_day,
    "baselines": suite_baselines,
    "profiles": suite_profiles,
    "scaling": suite_scaling,
}


def build_suite(name: str, budget: str = "quick") -> list:
    if name == "all":
        out = []
        for key in SUITE_BUILDERS:
            if key != "smoke":
                out += SUITE_BUILDERS[key](budget)
        return out
    if name not in SUITE_BUILDERS:
        raise ValueError(f"unknown suite {name!r}; choose from {sorted(SUITE_BUILDERS)} or 'all'")
    return SUITE_BUILDERS[name](budget)
