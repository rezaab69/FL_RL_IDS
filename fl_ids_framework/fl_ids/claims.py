"""Thesis claims, each checked against cached run results.

Every claim returns one of three statuses:
  REPRODUCED      the measured value satisfies the thesis statement (within the stated tolerance)
  NOT REPRODUCED  it does not
  NOT RUN         the runs it needs are not in the results folder yet
"""
from __future__ import annotations

from typing import Callable

CLAIMS: list = []


def claim(cid: str, text: str, source: str):
    def decorate(fn: Callable):
        CLAIMS.append((cid, text, source, fn))
        return fn
    return decorate


def _final(R: dict, name: str, key: str):
    rec = R.get(name)
    if not rec or "result" not in rec:
        return None
    return rec["result"]["final"].get(key)


def _per_class(R: dict, name: str, cls: str):
    rec = R.get(name)
    if not rec or "result" not in rec:
        return None
    return rec["result"]["final"].get("per_class_detection", {}).get(cls)


def _bench(R: dict, name: str, n: int, p: int, agg: str):
    rec = R.get(name)
    if not rec or "result" not in rec:
        return None
    for row in rec["result"]["rows"]:
        if row["n_clients"] == n and row["n_params"] == p and row["aggregator"] == agg:
            return row["median_seconds"]
    return None


def _missing(*names):
    return None, "not run: " + ", ".join(names)


# ---- centralised baselines and federated accuracy (Ch.4 Sec. 1-4-4, Table 4-7, Table 4-18)

@claim("C01", "Centralised PPO binary F1 is about 0.986 (tolerance 0.01)", "Ch.4 Sec. 1-4-4")
def _c01(R):
    v = _final(R, "baseline/binary/ppo", "f1")
    if v is None:
        return _missing("baseline/binary/ppo")
    return abs(v - 0.986) <= 0.01, f"F1={v:.4f}"


@claim("C02", "Federated clean F1 is within 0.01 of centralised PPO (thesis: 0.9842 vs 0.986)",
       "Ch.4 Table 4-7")
def _c02(R):
    fed = _final(R, "agg/clean/geometric_median+f1", "f1")
    cen = _final(R, "baseline/binary/ppo", "f1")
    if fed is None or cen is None:
        return _missing("agg/clean/geometric_median+f1", "baseline/binary/ppo")
    return abs(fed - cen) <= 0.01, f"federated F1={fed:.4f}, centralised F1={cen:.4f}"


@claim("C03", "Random forest scores at least the PPO F1 (thesis Table 4-18: 0.9990 vs 0.9860)",
       "Ch.4 Table 4-18")
def _c03(R):
    rf = _final(R, "baseline/binary/rf", "f1")
    ppo = _final(R, "baseline/binary/ppo", "f1")
    if rf is None or ppo is None:
        return _missing("baseline/binary/rf", "baseline/binary/ppo")
    return rf >= ppo, f"RF F1={rf:.4f}, PPO F1={ppo:.4f}"


@claim("C04", "Thesis profiles: legacy backup16 clean F1 is at least 0.98 (thesis: 0.9842)",
       "Ch.4 Table 4-7; backup16 code")
def _c04(R):
    v = _final(R, "profile/legacy_backup16/clean", "f1")
    if v is None:
        return _missing("profile/legacy_backup16/clean")
    return v >= 0.98, f"F1={v:.4f}"


# ---- poisoning and robust aggregation (Ch.4 Sec. 5-4, Tables 4-8, 4-9, 4-22, 4-23, 4-24)

@claim("C05", "Geometric median with F1 weighting keeps 98% of clean F1 under 60% model poisoning",
       "Ch.4 Table 4-9")
def _c05(R):
    clean = _final(R, "poison/clean/geometric_median+f1", "f1")
    att = _final(R, "poison/model_noise/60/geometric_median+f1", "f1")
    if clean is None or att is None:
        return _missing("poison/clean/geometric_median+f1", "poison/model_noise/60/geometric_median+f1")
    return att >= 0.98 * clean, f"clean={clean:.4f}, attacked={att:.4f}, ratio={att / clean:.3f}"


@claim("C06", "Unweighted FedAvg collapses (F1 drop of at least 0.10) under 60% model poisoning",
       "Ch.4 Table 4-24")
def _c06(R):
    clean = _final(R, "poison/clean/fedavg+none", "f1")
    att = _final(R, "poison/model_noise/60/fedavg+none", "f1")
    if clean is None or att is None:
        return _missing("poison/clean/fedavg+none", "poison/model_noise/60/fedavg+none")
    return clean - att >= 0.10, f"clean={clean:.4f}, attacked={att:.4f}, drop={clean - att:.4f}"


@claim("C07", "FedAvg with F1 weighting keeps 98% of clean F1 under 60% model poisoning",
       "Ch.4 Table 4-23 (FedAvg + F1)")
def _c07(R):
    clean = _final(R, "poison/clean/fedavg+f1", "f1")
    att = _final(R, "poison/model_noise/60/fedavg+f1", "f1")
    if clean is None or att is None:
        return _missing("poison/clean/fedavg+f1", "poison/model_noise/60/fedavg+f1")
    return att >= 0.98 * clean, f"clean={clean:.4f}, attacked={att:.4f}, ratio={att / clean:.3f}"


@claim("C08", "F1 weighting, not the aggregation rule, decides robustness: GM+F1 within 0.01 of FedAvg+F1",
       "Ch.4 Table 4-23; Sec. 9-4 conclusion")
def _c08(R):
    gm = _final(R, "poison/model_noise/60/geometric_median+f1", "f1")
    fa = _final(R, "poison/model_noise/60/fedavg+f1", "f1")
    if gm is None or fa is None:
        return _missing("poison/model_noise/60/geometric_median+f1", "poison/model_noise/60/fedavg+f1")
    return abs(gm - fa) <= 0.01, f"GM+F1={gm:.4f}, FedAvg+F1={fa:.4f}"


@claim("C09", "GM+F1 under 60% label flipping keeps F1 of about 0.9625 (tolerance 0.01)",
       "Ch.4 Table 4-8")
def _c09(R):
    v = _final(R, "poison/label_flip/60/geometric_median+f1", "f1")
    if v is None:
        return _missing("poison/label_flip/60/geometric_median+f1")
    return abs(v - 0.9625) <= 0.01, f"F1={v:.4f}"


@claim("C10", "Krum beats geometric median under 60% label flipping (thesis Table 4-22)", "Ch.4 Table 4-22")
def _c10(R):
    krum = _final(R, "poison/label_flip/60/krum+none", "f1")
    gm = _final(R, "poison/label_flip/60/geometric_median+none", "f1")
    if krum is None or gm is None:
        return _missing("poison/label_flip/60/krum+none", "poison/label_flip/60/geometric_median+none")
    return krum >= gm, f"Krum F1={krum:.4f}, GM F1={gm:.4f}"


@claim("C11", "Defence stack (gate + Z-score + exclusion) keeps 98% of clean F1 under 40% model poisoning",
       "Ch.3 Sec. 7-3; Ch.4 Sec. 5-4")
def _c11(R):
    clean = _final(R, "defense/clean/gate+zscore+exclusion", "f1")
    att = _final(R, "defense/model_noise/gate+zscore+exclusion", "f1")
    if clean is None or att is None:
        return _missing("defense/clean/gate+zscore+exclusion", "defense/model_noise/gate+zscore+exclusion")
    return att >= 0.98 * clean, f"clean={clean:.4f}, attacked={att:.4f}, ratio={att / clean:.3f}"


# ---- privacy (H3, Ch.1 and Ch.5 Sec. 4-3-5)

@claim("C12", "Differential privacy at epsilon 8 (update target, C=1) keeps 98% of the no-DP F1",
       "Ch.3 Algorithm 4")
def _c12(R):
    base = _final(R, "dp/nodp", "f1")
    v = _final(R, "dp/update_eps8_C1", "f1")
    if base is None or v is None:
        return _missing("dp/nodp", "dp/update_eps8_C1")
    return v >= 0.98 * base, f"no DP={base:.4f}, eps=8={v:.4f}"


@claim("C13", "Thesis-literal DP (noise on parameters, epsilon 1) keeps 98% of the no-DP F1",
       "Ch.3 Algorithm 4 (literal)")
def _c13(R):
    base = _final(R, "dp/nodp", "f1")
    v = _final(R, "dp/parameters_eps1_literal", "f1")
    if base is None or v is None:
        return _missing("dp/nodp", "dp/parameters_eps1_literal")
    return v >= 0.98 * base, f"no DP={base:.4f}, literal eps=1={v:.4f}"


@claim("C14", "H3 privacy direction: federated model leaks less membership signal than centralised PPO",
       "Ch.1 hypothesis 3")
def _c14(R):
    fed = _final(R, "agg/clean/geometric_median+f1", "mia_auc")
    cen = _final(R, "dp/centralized_ppo", "mia_auc")
    if fed is None or cen is None:
        return _missing("agg/clean/geometric_median+f1", "dp/centralized_ppo")
    return fed <= cen, f"federated MIA AUC={fed:.3f}, centralised MIA AUC={cen:.3f}"


# ---- zero-day generalisation (H1, Ch.4 Tables 4-11, 4-12, 4-25)

@claim("C15", "PPO detects held-out Port Scan at 95% or more (thesis: 97.72%)", "Ch.4 Table 4-11")
def _c15(R):
    v = _per_class(R, "zeroday/Port Scan/ppo", "Port Scan")
    if v is None:
        return _missing("zeroday/Port Scan/ppo")
    return v >= 0.95, f"detection={v:.4f}"


@claim("C16", "PPO detects held-out ICMP Flood at 5% or less (thesis: about 0%)", "Ch.4 Table 4-12")
def _c16(R):
    v = _per_class(R, "zeroday/ICMP Flood/ppo", "ICMP Flood")
    if v is None:
        return _missing("zeroday/ICMP Flood/ppo")
    return v <= 0.05, f"detection={v:.4f}"


@claim("C17", "H1: PPO detects held-out attacks at least as well as random forest on average",
       "Ch.4 Sec. 6-4 and Table 4-27")
def _c17(R):
    classes = sorted({k.split("/")[1] for k in R if k.startswith("zeroday/")})
    if not classes:
        return _missing("zeroday/*")
    ppo, rf = [], []
    for c in classes:
        p = _per_class(R, f"zeroday/{c}/ppo", c)
        r = _per_class(R, f"zeroday/{c}/rf", c)
        if p is not None and r is not None:
            ppo.append(p)
            rf.append(r)
    if not ppo:
        return _missing("zeroday/*/ppo and zeroday/*/rf")
    mp, mr = sum(ppo) / len(ppo), sum(rf) / len(rf)
    return mp >= mr, f"mean PPO detection={mp:.4f}, mean RF detection={mr:.4f} over {len(ppo)} classes"


# ---- aggregation cost (Ch.4 Sec. 7-4, Tables 4-14, 4-16)

@claim("C18", "Geometric median overhead vs FedAvg at 100 clients is at most 12.4x (thesis Table 4-16)",
       "Ch.4 Table 4-16")
def _c18(R):
    rows = "scaling/bench"
    gm = _bench(R, rows, 100, 23330, "geometric_median")
    fa = _bench(R, rows, 100, 23330, "fedavg")
    if gm is None or fa is None:
        return _missing(rows)
    return gm / fa <= 12.4, f"GM={gm * 1000:.2f} ms, FedAvg={fa * 1000:.2f} ms, ratio={gm / fa:.1f}x"


@claim("C19", "Geometric median time grows at most 20x from 5 to 100 clients (thesis: near-linear)",
       "Ch.4 Table 4-14")
def _c19(R):
    rows = "scaling/bench"
    small = _bench(R, rows, 5, 23330, "geometric_median")
    large = _bench(R, rows, 100, 23330, "geometric_median")
    if small is None or large is None:
        return _missing(rows)
    return large / small <= 20, f"5 clients={small * 1000:.2f} ms, 100 clients={large * 1000:.2f} ms"


# ---- hyper-parameter sensitivity (Ch.4 Table 4-4 vs Ch.3)

@claim("C20", "PPO hyper-parameter choice barely changes federated F1 (thesis_table44 vs thesis_spec, 0.01)",
       "Ch.3 Sec. 3-3-3 vs Ch.4 Table 4-4")
def _c20(R):
    a = _final(R, "profile/thesis_spec/clean", "f1")
    b = _final(R, "profile/thesis_table44/clean", "f1")
    if a is None or b is None:
        return _missing("profile/thesis_spec/clean", "profile/thesis_table44/clean")
    return abs(a - b) <= 0.01, f"thesis_spec={a:.4f}, thesis_table44={b:.4f}"


def evaluate(R: dict) -> list:
    rows = []
    for cid, text, source, fn in CLAIMS:
        try:
            ok, measured = fn(R)
        except Exception as exc:
            ok, measured = None, f"error: {type(exc).__name__}: {exc}"
        status = "NOT RUN" if ok is None else ("REPRODUCED" if ok else "NOT REPRODUCED")
        rows.append({"id": cid, "claim": text, "source": source, "status": status, "measured": measured})
    return rows
