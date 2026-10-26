"""RL agents: actor-critic PPO (thesis Sec. 3-3-3) and a DQN baseline, on a sample-sequence environment.

Environment: each step reveals one training sample, the agent acts, and receives the reward
R = alpha * R_detection - beta * R_false_positive - gamma_resp * R_response (thesis reward form).
The next sample does not depend on the action, as in backup16's IntrusionDetectionEnv.
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
from torch.distributions import Categorical

from .config import AgentConfig


def n_actions(cfg: AgentConfig) -> int:
    return 2 if cfg.actions == "binary" else 5


def reward(cfg: AgentConfig, action: int, label: int) -> float:
    """Action 0 is NO_ACTION; any other action flags the sample as an attack."""
    detect = action != 0
    if cfg.actions == "binary":
        cost = cfg.action_costs[1] if detect else 0.0
    else:
        cost = cfg.action_costs[action]
    if label == 1:
        r = cfg.alpha if detect else -cfg.miss_penalty
    else:
        r = -cfg.beta if detect else 0.0
    return r - cfg.gamma_resp * cost


class SampleEnv:
    """Sequential environment over a pool of samples (episodes of episode_len steps)."""

    def __init__(self, X: np.ndarray, y: np.ndarray, cfg: AgentConfig, rng: np.random.Generator):
        if len(X) == 0:
            raise ValueError("empty training pool")
        self.X, self.y, self.cfg, self.rng = X, y, cfg, rng
        self.t = 0
        self.obs = self._draw()

    def _draw(self) -> np.ndarray:
        self.i = int(self.rng.integers(len(self.X)))
        return self.X[self.i]

    def step(self, action: int):
        r = reward(self.cfg, action, int(self.y[self.i]))
        self.t += 1
        done = self.t >= self.cfg.episode_len
        if done:
            self.t = 0
        self.obs = self._draw()
        return r, done


def _mlp(d_in: int, hidden, d_out: int) -> nn.Sequential:
    layers, d = [], d_in
    for h in hidden:
        layers += [nn.Linear(d, h), nn.ReLU()]
        d = h
    layers.append(nn.Linear(d, d_out))
    return nn.Sequential(*layers)


class ActorCritic(nn.Module):
    """Separate actor (policy) and critic (value) networks, both MLPs with ReLU hidden layers."""

    def __init__(self, obs_dim: int, n_act: int, hidden):
        super().__init__()
        self.actor = _mlp(obs_dim, hidden, n_act)
        self.critic = _mlp(obs_dim, hidden, 1)

    def forward(self, x):
        return self.actor(x), self.critic(x).squeeze(-1)


def _param_list(model: ActorCritic, include_critic: bool):
    modules = [model.actor] + ([model.critic] if include_critic else [])
    return [p for m in modules for p in m.parameters()]


def get_vector(model: ActorCritic, include_critic: bool = False) -> np.ndarray:
    return torch.cat([p.detach().reshape(-1) for p in _param_list(model, include_critic)]).double().cpu().numpy()


def set_vector(model: ActorCritic, vec: np.ndarray, include_critic: bool = False) -> None:
    flat = torch.as_tensor(np.asarray(vec), dtype=torch.float32)
    offset = 0
    with torch.no_grad():
        for p in _param_list(model, include_critic):
            n = p.numel()
            p.copy_(flat[offset:offset + n].view_as(p))
            offset += n
    if offset != flat.numel():
        raise ValueError(f"vector length {flat.numel()} does not match parameters {offset}")


def ppo_train(model: ActorCritic, opt: torch.optim.Optimizer, env: SampleEnv, cfg: AgentConfig,
              steps: int) -> dict:
    """Run `steps` environment steps in rollouts, with clipped-surrogate PPO updates.

    Loss (minimised): -L_CLIP + vf_coef * L_VF - ent_coef * H, the negated thesis objective.
    """
    done_total, updates, rewards = 0, 0, []
    while done_total < steps:
        T = min(cfg.rollout_steps, steps - done_total)
        obs_b = np.zeros((T, env.obs.shape[0]), dtype=np.float32)
        act_b = np.zeros(T, dtype=np.int64)
        logp_b = np.zeros(T, dtype=np.float32)
        val_b = np.zeros(T, dtype=np.float32)
        rew_b = np.zeros(T, dtype=np.float32)
        done_b = np.zeros(T, dtype=np.float32)
        with torch.no_grad():
            for t in range(T):
                logits, v = model(torch.as_tensor(env.obs, dtype=torch.float32).unsqueeze(0))
                dist = Categorical(logits=logits[0])
                a = dist.sample()
                obs_b[t] = env.obs
                act_b[t] = int(a)
                logp_b[t] = float(dist.log_prob(a))
                val_b[t] = float(v[0])
                r, d = env.step(int(a))
                rew_b[t] = r
                done_b[t] = float(d)
            last_v = float(model(torch.as_tensor(env.obs, dtype=torch.float32).unsqueeze(0))[1][0])

        # generalised advantage estimation
        adv = np.zeros(T, dtype=np.float32)
        gae = 0.0
        for t in reversed(range(T)):
            nonterminal = 1.0 - done_b[t]
            next_v = last_v if t == T - 1 else float(val_b[t + 1])
            delta = rew_b[t] + cfg.gamma * next_v * nonterminal - val_b[t]
            gae = delta + cfg.gamma * cfg.gae_lambda * nonterminal * gae
            adv[t] = gae
        ret = adv + val_b
        adv = (adv - adv.mean()) / (adv.std() + 1e-8)

        obs_t = torch.as_tensor(obs_b)
        act_t = torch.as_tensor(act_b)
        logp_old = torch.as_tensor(logp_b)
        adv_t = torch.as_tensor(adv)
        ret_t = torch.as_tensor(ret)
        for _ in range(cfg.epochs):
            perm = torch.randperm(T)
            for s in range(0, T, cfg.minibatch):
                mb = perm[s:s + cfg.minibatch]
                logits, v = model(obs_t[mb])
                dist = Categorical(logits=logits)
                ratio = torch.exp(dist.log_prob(act_t[mb]) - logp_old[mb])
                a = adv_t[mb]
                surrogate = torch.min(ratio * a, torch.clamp(ratio, 1 - cfg.clip, 1 + cfg.clip) * a)
                loss_v = ((v - ret_t[mb]) ** 2).mean()
                loss = -surrogate.mean() + cfg.vf_coef * loss_v - cfg.ent_coef * dist.entropy().mean()
                opt.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), cfg.max_grad_norm)
                opt.step()
                updates += 1
        rewards.extend(rew_b.tolist())
        done_total += T
    return {"updates": updates, "mean_reward": float(np.mean(rewards)) if rewards else 0.0}


@torch.no_grad()
def predict_actions(model: ActorCritic, X: np.ndarray, batch: int = 8192) -> np.ndarray:
    out = np.empty(len(X), dtype=np.int64)
    for s in range(0, len(X), batch):
        logits, _ = model(torch.as_tensor(X[s:s + batch], dtype=torch.float32))
        out[s:s + batch] = logits.argmax(dim=1).numpy()
    return out


@torch.no_grad()
def attack_probability(model: ActorCritic, X: np.ndarray, batch: int = 8192) -> np.ndarray:
    """P(action != NO_ACTION) for each row, used by the membership-inference attack."""
    out = np.empty(len(X), dtype=np.float64)
    for s in range(0, len(X), batch):
        logits, _ = model(torch.as_tensor(X[s:s + batch], dtype=torch.float32))
        out[s:s + batch] = 1.0 - torch.softmax(logits, dim=1)[:, 0].numpy()
    return out


class QNet(nn.Module):
    def __init__(self, obs_dim: int, n_act: int, hidden):
        super().__init__()
        self.net = _mlp(obs_dim, hidden, n_act)

    def forward(self, x):
        return self.net(x)


def dqn_train(q: QNet, target: QNet, opt: torch.optim.Optimizer, env: SampleEnv, cfg: AgentConfig,
              steps: int, rng: np.random.Generator, n_act: int, batch: int = 128,
              capacity: int = 50000, target_every: int = 500) -> dict:
    """Deep Q-learning with a replay buffer and epsilon-greedy exploration (centralised baseline)."""
    d = env.obs.shape[0]
    buf_o = np.zeros((capacity, d), dtype=np.float32)
    buf_n = np.zeros((capacity, d), dtype=np.float32)
    buf_a = np.zeros(capacity, dtype=np.int64)
    buf_r = np.zeros(capacity, dtype=np.float32)
    buf_d = np.zeros(capacity, dtype=np.float32)
    filled, pos = 0, 0
    for step in range(steps):
        eps = max(0.05, 1.0 - step / (0.5 * steps))
        o = env.obs.copy()
        if rng.random() < eps:
            a = int(rng.integers(n_act))
        else:
            with torch.no_grad():
                a = int(q(torch.as_tensor(o).unsqueeze(0)).argmax())
        r, done = env.step(a)
        buf_o[pos], buf_a[pos], buf_r[pos], buf_n[pos], buf_d[pos] = o, a, r, env.obs, float(done)
        pos = (pos + 1) % capacity
        filled = min(filled + 1, capacity)
        if filled >= batch:
            idx = rng.integers(filled, size=batch)
            qs = q(torch.as_tensor(buf_o[idx])).gather(1, torch.as_tensor(buf_a[idx]).unsqueeze(1)).squeeze(1)
            with torch.no_grad():
                nxt = target(torch.as_tensor(buf_n[idx])).max(dim=1).values
                y = torch.as_tensor(buf_r[idx]) + cfg.gamma * (1.0 - torch.as_tensor(buf_d[idx])) * nxt
            loss = nn.functional.smooth_l1_loss(qs, y)
            opt.zero_grad()
            loss.backward()
            opt.step()
        if step % target_every == 0:
            target.load_state_dict(q.state_dict())
    return {"steps": steps}


@torch.no_grad()
def q_attack_probability(q: QNet, X: np.ndarray, batch: int = 8192) -> np.ndarray:
    out = np.empty(len(X), dtype=np.float64)
    for s in range(0, len(X), batch):
        out[s:s + batch] = 1.0 - torch.softmax(q(torch.as_tensor(X[s:s + batch])), dim=1)[:, 0].numpy()
    return out


@torch.no_grad()
def q_predict_actions(q: QNet, X: np.ndarray, batch: int = 8192) -> np.ndarray:
    out = np.empty(len(X), dtype=np.int64)
    for s in range(0, len(X), batch):
        out[s:s + batch] = q(torch.as_tensor(X[s:s + batch])).argmax(dim=1).numpy()
    return out
