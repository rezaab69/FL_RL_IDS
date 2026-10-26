# Thesis reproduction report

Generated 2026-10-26 02:32 from 8 cached runs.

## Thesis claims

| ID | Claim | Source | Status | Measured |
|---|---|---|---|---|
| C01 | Centralised PPO binary F1 is about 0.986 (tolerance 0.01) | Ch.4 Sec. 1-4-4 | NOT RUN | not run: baseline/binary/ppo |
| C02 | Federated clean F1 is within 0.01 of centralised PPO (thesis: 0.9842 vs 0.986) | Ch.4 Table 4-7 | NOT RUN | not run: agg/clean/geometric_median+f1, baseline/binary/ppo |
| C03 | Random forest scores at least the PPO F1 (thesis Table 4-18: 0.9990 vs 0.9860) | Ch.4 Table 4-18 | NOT RUN | not run: baseline/binary/rf, baseline/binary/ppo |
| C04 | Thesis profiles: legacy backup16 clean F1 is at least 0.98 (thesis: 0.9842) | Ch.4 Table 4-7; backup16 code | NOT RUN | not run: profile/legacy_backup16/clean |
| C05 | Geometric median with F1 weighting keeps 98% of clean F1 under 60% model poisoning | Ch.4 Table 4-9 | NOT RUN | not run: poison/clean/geometric_median+f1, poison/model_noise/60/geometric_median+f1 |
| C06 | Unweighted FedAvg collapses (F1 drop of at least 0.10) under 60% model poisoning | Ch.4 Table 4-24 | NOT RUN | not run: poison/clean/fedavg+none, poison/model_noise/60/fedavg+none |
| C07 | FedAvg with F1 weighting keeps 98% of clean F1 under 60% model poisoning | Ch.4 Table 4-23 (FedAvg + F1) | NOT RUN | not run: poison/clean/fedavg+f1, poison/model_noise/60/fedavg+f1 |
| C08 | F1 weighting, not the aggregation rule, decides robustness: GM+F1 within 0.01 of FedAvg+F1 | Ch.4 Table 4-23; Sec. 9-4 conclusion | NOT RUN | not run: poison/model_noise/60/geometric_median+f1, poison/model_noise/60/fedavg+f1 |
| C09 | GM+F1 under 60% label flipping keeps F1 of about 0.9625 (tolerance 0.01) | Ch.4 Table 4-8 | NOT RUN | not run: poison/label_flip/60/geometric_median+f1 |
| C10 | Krum beats geometric median under 60% label flipping (thesis Table 4-22) | Ch.4 Table 4-22 | NOT RUN | not run: poison/label_flip/60/krum+none, poison/label_flip/60/geometric_median+none |
| C11 | Defence stack (gate + Z-score + exclusion) keeps 98% of clean F1 under 40% model poisoning | Ch.3 Sec. 7-3; Ch.4 Sec. 5-4 | NOT RUN | not run: defense/clean/gate+zscore+exclusion, defense/model_noise/gate+zscore+exclusion |
| C12 | Differential privacy at epsilon 8 (update target, C=1) keeps 98% of the no-DP F1 | Ch.3 Algorithm 4 | NOT RUN | not run: dp/nodp, dp/update_eps8_C1 |
| C13 | Thesis-literal DP (noise on parameters, epsilon 1) keeps 98% of the no-DP F1 | Ch.3 Algorithm 4 (literal) | NOT RUN | not run: dp/nodp, dp/parameters_eps1_literal |
| C14 | H3 privacy direction: federated model leaks less membership signal than centralised PPO | Ch.1 hypothesis 3 | NOT RUN | not run: agg/clean/geometric_median+f1, dp/centralized_ppo |
| C15 | PPO detects held-out Port Scan at 95% or more (thesis: 97.72%) | Ch.4 Table 4-11 | NOT RUN | not run: zeroday/Port Scan/ppo |
| C16 | PPO detects held-out ICMP Flood at 5% or less (thesis: about 0%) | Ch.4 Table 4-12 | NOT RUN | not run: zeroday/ICMP Flood/ppo |
| C17 | H1: PPO detects held-out attacks at least as well as random forest on average | Ch.4 Sec. 6-4 and Table 4-27 | NOT RUN | not run: zeroday/* |
| C18 | Geometric median overhead vs FedAvg at 100 clients is at most 12.4x (thesis Table 4-16) | Ch.4 Table 4-16 | NOT RUN | not run: scaling/bench |
| C19 | Geometric median time grows at most 20x from 5 to 100 clients (thesis: near-linear) | Ch.4 Table 4-14 | NOT RUN | not run: scaling/bench |
| C20 | PPO hyper-parameter choice barely changes federated F1 (thesis_table44 vs thesis_spec, 0.01) | Ch.3 Sec. 3-3-3 vs Ch.4 Table 4-4 | NOT RUN | not run: profile/thesis_spec/clean, profile/thesis_table44/clean |

## Runs

| Run | F1 | FPR | FNR | Recall | MIA AUC | Seconds |
|---|---|---|---|---|---|---|
| poison/model_noise/20/fedavg+f1 | 0.3881 | 0.2243 | 0.7395 | 0.2605 | 0.559 | 28.61 |
| poison/model_noise/20/fedavg+none | 0.1873 | 0.2461 | 0.8874 | 0.1126 | 0.577 | 40.07 |
| poison/model_noise/20/geometric_median+f1 | 0.9453 | 0.0872 | 0.0751 | 0.9249 | 0.479 | 28.3 |
| poison/model_noise/20/geometric_median+none | 0.9447 | 0.0841 | 0.0774 | 0.9226 | 0.490 | 27.51 |
| poison/model_noise/20/krum+none | 0.8936 | 0.0966 | 0.1638 | 0.8362 | 0.490 | 27.89 |
| poison/model_noise/20/median+none | 0.9448 | 0.0903 | 0.0751 | 0.9249 | 0.485 | 27.56 |
| poison/model_noise/20/multi_krum+none | 0.9453 | 0.0872 | 0.0751 | 0.9249 | 0.481 | 29.22 |
| poison/model_noise/20/trimmed_mean+none | 0.1873 | 0.2461 | 0.8874 | 0.1126 | 0.577 | 27.95 |
