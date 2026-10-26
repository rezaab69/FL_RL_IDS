"""Configuration for every experiment: data, agent, federation, attack and privacy settings."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Optional

DEFAULT_CSV = r"F:\C File\Trae\flow_model\flow_meter_rl_fl_5\db_o\ACI-IoT-2023.csv"
FIVE_ACTIONS = ("NO_ACTION", "BLOCK", "ISOLATE", "RATE_LIMIT", "INVESTIGATE")


@dataclass
class DataConfig:
    csv_path: str = DEFAULT_CSV
    label_col: str = "Label"
    drop_cols: tuple = ("Connection Type",)
    task: str = "binary"                  # binary: benign vs attack; multiclass: every label
    max_rows: Optional[int] = None        # stratified subsample; None uses the whole file
    test_fraction: float = 0.2
    smote: bool = True
    smote_cap: int = 5000                 # classes below this size are oversampled up to it
    partition: str = "iid"                # iid | label_skew | dirichlet
    dirichlet_alpha: float = 0.5
    holdout_class: Optional[str] = None   # zero-day: removed from training, kept in test
    validation_fraction: float = 0.1      # clean per-client validation split, never trained on
    seed: int = 42


@dataclass
class AgentConfig:
    actions: str = "binary"               # binary: NO_ACTION/BLOCK; five: thesis action set
    hidden: tuple = (256, 128, 64)
    lr: float = 3e-4
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip: float = 0.2
    ent_coef: float = 0.01
    vf_coef: float = 0.5
    max_grad_norm: float = 1.0
    rollout_steps: int = 2048
    minibatch: int = 64
    epochs: int = 10
    episode_len: int = 256
    alpha: float = 1.0                    # reward for detecting an attack
    beta: float = 1.0                     # penalty for a false alarm
    gamma_resp: float = 0.1               # weight of the response cost
    miss_penalty: float = 0.0             # not defined in the thesis; 0 by default
    action_costs: tuple = (0.0, 1.0, 2.0, 1.0, 1.0)  # NO_ACTION, BLOCK, ISOLATE, RATE_LIMIT, INVESTIGATE


@dataclass
class FedConfig:
    n_clients: int = 10
    rounds: int = 10
    local_steps: int = 20000              # PPO environment steps per client per round
    aggregator: str = "geometric_median"  # fedavg | geometric_median | krum | multi_krum | trimmed_mean | median
    weighting: str = "none"               # none | f1 | accuracy | datasize | f1_minmax | accuracy_minmax
    gate: str = "none"                    # none | accuracy | f1: accepted when metric >= gate_threshold
    gate_threshold: float = 0.85
    anomaly_filter: str = "none"          # none | zscore | iqr
    anomaly_limit: float = 3.0
    anomaly_fraction: float = 0.05
    exclusion_patience: int = 0           # 0 disables; thesis: 3 consecutive failures
    blend_beta: float = 1.0               # client policy <- (1-beta)*local + beta*global; thesis: 0.3
    share_critic: bool = False            # thesis: critic stays local
    krum_f: Optional[int] = None          # assumed malicious count; None uses the true count
    trim_ratio: float = 0.1


@dataclass
class AttackConfig:
    kind: str = "none"                    # none | label_flip | model_noise | sign_flip | scaling
    n_malicious: int = 0
    flip_fraction: float = 0.5
    noise_std: float = 10.0
    scale_factor: float = 10.0


@dataclass
class PrivacyConfig:
    dp: bool = False
    epsilon: float = 1.0
    delta: float = 1e-5
    clip_norm: float = 1.0                # C: L2 clip of the update
    target: str = "update"                # update: noise on the clipped update | parameters: thesis literal
    sensitivity: Optional[float] = None   # None means clip_norm


@dataclass
class ExperimentConfig:
    name: str
    kind: str = "federated"               # federated | centralized | aggregation_bench
    model: str = "ppo"                    # centralized only: ppo | dqn | rf | dt | xgb | mlp
    seed: int = 42
    data: DataConfig = field(default_factory=DataConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    fed: FedConfig = field(default_factory=FedConfig)
    attack: AttackConfig = field(default_factory=AttackConfig)
    privacy: PrivacyConfig = field(default_factory=PrivacyConfig)
    bench: dict = field(default_factory=dict)  # aggregation_bench: n_clients, n_params, repeats

    def to_dict(self) -> dict:
        return asdict(self)

    def key(self) -> str:
        blob = json.dumps(self.to_dict(), sort_keys=True, default=str).encode()
        return hashlib.sha1(blob).hexdigest()[:12]


_SECTIONS = {
    "data": DataConfig,
    "agent": AgentConfig,
    "fed": FedConfig,
    "attack": AttackConfig,
    "privacy": PrivacyConfig,
}


def _tuplify(section: dict) -> dict:
    return {k: tuple(v) if isinstance(v, list) else v for k, v in section.items()}


def from_dict(d: dict) -> ExperimentConfig:
    """Rebuild an ExperimentConfig from the dictionary produced by to_dict()."""
    kwargs = {}
    for k, v in d.items():
        kwargs[k] = _SECTIONS[k](**_tuplify(v)) if k in _SECTIONS else v
    return ExperimentConfig(**kwargs)
