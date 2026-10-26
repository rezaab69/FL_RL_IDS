# FL-PPO intrusion-detection testing framework

A test bench for the algorithms and scenarios in the thesis *Design of a secure intrusion detection system using artificial intelligence* (F-PPO-IDS, `F:\FL_RL_IDS\FL_RL_IDS.pdf`). It does not wrap the old scripts. It reimplements each algorithm from the thesis, so every component can be varied, tested and compared.

## What is covered

| Thesis part | Implemented in | Where it is exercised |
|---|---|---|
| Actor-critic PPO agent, clipped surrogate, GAE, entropy, value loss (Sec. 3-3-3) | `agents.py` | `ppo_train`; every federated and centralised PPO run |
| Reward R = alpha R_det - beta R_fp - gamma R_resp, binary and five-action sets | `agents.py` (`reward`) | all PPO runs; `actions` option |
| DQN baseline | `agents.py` (`dqn_train`) | centralised baselines and zero-day |
| Federated protocol: local training, blend with beta, aggregation, redistribution (Alg. 1, Eq. 15) | `federation.py` (`run_federated`) | every federated run |
| Aggregators: FedAvg (weighted), geometric median (Weiszfeld, weighted), Krum, Multi-Krum, trimmed mean, coordinate median (Alg. 3) | `aggregators.py` | all poisoning and aggregator suites |
| Weights from F1, accuracy, data size, min-max normalised variants (Eq. 2) | `defenses.py` (`client_weights`) | `weighting` option |
| Quality gate: accuracy or F1 threshold, 85% by default in the thesis (Sec. 7-3) | `defenses.py` | `gate` option |
| Anomaly filter: Z-score (|Z| > 3, > 5% of parameters) or IQR | `defenses.py` (`anomaly_flags`) | `anomaly_filter` option |
| Exclusion after k consecutive failures, readmission on pass | `defenses.py` (`ExclusionTracker`) | `exclusion_patience` option |
| Gaussian differential privacy, sigma = sqrt(2 ln(1.25/delta)) Delta / eps (Alg. 4) | `privacy.py` | `privacy` options; suite `dp` |
| Attacks: label flipping, Gaussian model noise (std 10), sign flip, scaling | `attacks.py` | `attack` options; suites `poisoning`, `defenses`, `dp` |
| Non-IID (label-skew), IID, Dirichlet partitions | `data.py` (`partition`) | `partition` option |
| Zero-day protocol: hold out one attack class from training | `data.py` (`holdout_class`) | suite `zero_day` |
| Classical baselines: random forest, decision tree, XGBoost, MLP | `federation.py` (`run_centralized`) | suites `baselines`, `zero_day` |
| Detection metrics: F1, precision, recall, FPR, FNR, per-class detection | `metrics.py` | every run |
| Membership-inference AUC (privacy measurement, hypothesis H3) | `metrics.py`, `federation.py` | every run |
| Aggregation cost: time versus clients and model size | `federation.py` (`run_aggregation_bench`) | suite `scaling` |
| Thesis claims with tolerances and verdicts | `claims.py` | `python -m fl_ids report` |

## Layout

```
fl_ids_framework/
  fl_ids/            the framework (config, data, agents, aggregators, defenses, attacks,
                     privacy, metrics, federation, scenarios, runner, claims, report, __main__)
  tests/             unit and pipeline tests (pytest), synthetic data only
  cache/             preprocessed dataset (created on first run, about 400 MB)
  results/           one JSON per run (configuration, per-round history, final metrics)
  reports/report.md  generated report
```

## Requirements

Python 3.10 or newer with `numpy`, `pandas`, `torch`, `scikit-learn`, `imbalanced-learn`, `xgboost`, and `pytest` for the tests. The versions used in this session: Python 3.13.1, torch 2.8.0 (CPU), scikit-learn 1.7.2, imbalanced-learn 0.14.0, xgboost 3.0.5, pandas 2.3.2, numpy 2.2.6, pytest 8.3.4.

## Quick start

```bat
cd "F:\FL_RL_IDS\fl_ids_framework"
python -m fl_ids test                              # 37 unit and pipeline tests, about 1 minute
python -m fl_ids data                              # loads the dataset (first run builds the cache)
python -m fl_ids list                              # suites, budgets, profiles
python -m fl_ids run smoke --budget smoke          # 3 runs, seconds to minutes
python -m fl_ids run poisoning --budget quick --only "poison/model_noise/60"
python -m fl_ids report                            # reports/report.md with claim verdicts
```

The dataset path is set in `fl_ids/config.py` (`DEFAULT_CSV`). The cache folder can be moved with the environment variable `FL_IDS_CACHE`, and results with `FL_IDS_RESULTS`.

## Suites

| Suite | Runs (quick budget) | Tests |
|---|---|---|
| `smoke` | 3 | Pipeline works end to end |
| `aggregators` | 8 | Clean-data accuracy of each aggregator and weighting |
| `poisoning` | 56 | Label flipping and model noise at 20/40/60% malicious clients, for each aggregator (Tables 4-8, 4-9, 4-22, 4-23) |
| `defenses` | 8 | Gate, Z-score filter and exclusion, alone and combined, under 40% model noise |
| `dp` | 6 | No DP, DP on updates at several epsilons and clip norms, the thesis-literal noise on parameters, and a centralised PPO for the membership comparison |
| `zero_day` | 18 (quick) / 66 (full) | Each held-out attack class, for PPO, DQN, RF, DT, XGBoost and MLP (Tables 4-11, 4-12, 4-25) |
| `baselines` | 10 | Centralised detectors on binary and multiclass labels (Table 4-18) |
| `profiles` | 8 | thesis_spec, thesis_table44, legacy_backup16 and plain FedAvg, clean and under 60% model noise |
| `scaling` | 1 | Aggregator time versus number of clients and model size (Tables 4-14 to 4-16) |
| `all` | | Every suite except `smoke` |

Counts are for the quick budget. Use `--only REGEX` to run part of a suite. Each configuration name is printed, so the regex can select by name.

## Profiles (which algorithm rules to use)

| Profile | Meaning |
|---|---|
| `thesis_spec` | Chapter 3 rules: lambda 0.95, c1 0.5, c2 0.01, blend beta 0.3, critic local, accuracy gate 85%, Z-score filter, exclusion after 3 failures, F1 weighting |
| `thesis_table44` | Table 4-4 PPO values (gamma 0.01, lambda 0.1, clip 0.1, entropy 0.07, value 0.1, gradient norm 0.7) with the thesis_spec federation rules |
| `legacy_backup16` | What backup16's `new2` script does: gamma 0.01, lambda 0.1, clip 0.2, no entropy, F1 gate at 0.3, no blend, shared critic, no filter, no exclusion |
| `plain_fedavg` | Classic federated averaging with no defence |
| `framework_default` | The framework's defaults |

## Budgets

| Budget | Rows | Rounds | PPO steps per client per round | Use |
|---|---|---|---|---|
| `smoke` | 6,000 | 2 | 1,024 | Checks that code runs |
| `quick` | 30,000 | 3 | 4,096 | Exploration |
| `standard` | 200,000 | 5 | 8,192 | Confirmatory |
| `full` | all 1,231,411 | 10 | 20,000 | The thesis budget |

Full-budget federated runs with 10 clients take hours each. The poisoning suite at full budget is days of compute. Run subsets with `--only`. Results are cached by configuration hash, so an interrupted run resumes where it stopped.

## Claims checked

`claims.py` lists the thesis statements with their sources. `python -m fl_ids report` evaluates each one against the cached results. It reports REPRODUCED, NOT REPRODUCED, or NOT RUN for claims whose runs are missing.

| ID | Claim | Source |
|---|---|---|
| C01 | Centralised PPO binary F1 about 0.986 | Ch.4 Sec. 1-4-4 |
| C02 | Federated clean F1 within 0.01 of centralised PPO | Table 4-7 |
| C03 | Random forest F1 at least PPO F1 | Table 4-18 |
| C04 | legacy_backup16 clean F1 at least 0.98 | Table 4-7 and backup16 code |
| C05 | GM with F1 weighting keeps 98% of clean F1 under 60% model noise | Table 4-9 |
| C06 | Unweighted FedAvg drops by at least 0.10 under 60% model noise | Table 4-24 |
| C07 | FedAvg with F1 weighting keeps 98% under 60% model noise | Table 4-23 |
| C08 | F1 weighting decides robustness: GM+F1 within 0.01 of FedAvg+F1 | Table 4-23 |
| C09 | GM+F1 under 60% label flipping about 0.9625 | Table 4-8 |
| C10 | Krum beats GM under 60% label flipping | Table 4-22 |
| C11 | Gate + Z-score + exclusion keeps 98% under 40% model noise | Sec. 7-3, Sec. 5-4 |
| C12 | DP at epsilon 8 keeps 98% of no-DP F1 | Algorithm 4 |
| C13 | Thesis-literal DP (noise on parameters) keeps 98% of no-DP F1 | Algorithm 4 (literal) |
| C14 | Federated model leaks less membership signal than centralised PPO | Hypothesis H3 |
| C15 | PPO detects held-out Port Scan at 95% or more | Table 4-11 |
| C16 | PPO detects held-out ICMP Flood at 5% or less | Table 4-12 |
| C17 | PPO detects held-out attacks at least as well as RF on average | Sec. 6-4, Table 4-27 |
| C18 | GM overhead versus FedAvg at 100 clients at most 12.4x | Table 4-16 |
| C19 | GM time grows at most 20x from 5 to 100 clients | Table 4-14 |
| C20 | PPO hyper-parameter choice changes federated F1 by at most 0.01 | Table 4-4 versus Ch.3 |

## Assumptions and design decisions

These are the points where the thesis is silent, or where the thesis and the code disagree. Each one is a setting in the configuration, so you can change it.

1. **Reward miss penalty.** The thesis reward has three terms and no penalty for a missed attack. `miss_penalty` is 0 by default.
2. **Action costs** for the five-action set (NO_ACTION 0, BLOCK 1, ISOLATE 2, RATE_LIMIT 1, INVESTIGATE 1) are assumptions. The thesis gives no values.
3. **Discount factor.** The thesis does not give gamma for `thesis_spec`, so 0.99 is used. `thesis_table44` and `legacy_backup16` use 0.01 as in Table 4-4 and backup16.
4. **Environment dynamics.** The next sample does not depend on the action, as in backup16. The thesis describes a network whose state changes with the response. The framework does not model that.
5. **Validation.** Each client keeps 10% of its own rows as a clean validation set that it never trains on. Clients report the validation metrics of the vector they send, before differential privacy is applied. This is how the thesis's accuracy gate is described. backup16 uses the tail of the training data instead.
6. **Differential privacy.** The default target clips each update to C and adds Gaussian noise with the classic calibration, so the sensitivity is C. The thesis-literal target adds noise to the raw parameters. With the classic calibration and epsilon 1, the noise standard deviation is about 4.85 times the sensitivity, far larger than any parameter. The `dp` suite shows this.
7. **Privacy accounting** is per round. There is no composition across rounds, so the epsilon values are not total budgets.
8. **SMOTE** is applied to the training pool before partitioning, as the thesis does. This means synthetic rows are created from all clients' data at the server. A strict federated setting would not allow that.
9. **Membership-inference AUC** scores each row by the model's confidence in its true attack-or-benign label. 0.5 means no measurable leakage. Members are training rows, and non-members are test rows. Synthetic SMOTE rows can appear among the members.
10. **Z-score limit.** With population standard deviation, the largest possible |Z| for n clients is (n-1)/sqrt(n). For 8 clients that is 2.47, so the rule |Z| > 3 cannot fire. The rule needs at least 11 clients. This is a property of the thesis's rule, and a unit test checks it.
11. **Weights** are used only by FedAvg and the geometric median, as in the thesis. Krum, Multi-Krum, trimmed mean and the coordinate median are unweighted.
12. **Dataset.** The CSV has 1,231,411 rows and 12 distinct labels (benign plus 11 attack types). Table 4-1 says 411,231 records, and the text says 13 classes. The class counts in Tables 4-11 and 4-12 match the CSV exactly, so the thesis's dataset is this file.

## Reproducibility

Every run takes a seed (`seed`, default 42). Data splits, client partitions, malicious-client selection, PPO sampling and the membership-inference sample all derive from it. The seed does not make two runs identical across machines with different thread counts, because PyTorch and BLAS can reorder floating-point sums.

## Status of this build

- Unit and pipeline tests: 37 pass (`python -m fl_ids test`).
- Smoke suite on the real dataset: runs end to end. Also checked: one model-noise poisoning run and two zero-day runs at smoke budget.
- Not run here: the quick, standard and full grids. Their numbers are not in this README. Run them, then `python -m fl_ids report`.

## Limitations

- Runs are not comparable to the thesis's absolute numbers unless they use the full budget.
- The reward, environment and action costs are assumptions where the thesis is silent (see above).
- Measured aggregation times depend on the machine.
- Membership inference is one attack. It does not test the server's view of individual client updates, which would be a stronger test.

## Extending

- A new algorithm: add a function in its own module, then a branch in `runner.run_one`.
- A new scenario: add a function to `scenarios.py` that returns configurations and register it in `SUITE_BUILDERS`.
- A new claim: add a function decorated with `@claim` in `claims.py` that returns `(ok, measured)`.
