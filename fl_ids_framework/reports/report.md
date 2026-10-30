# Thesis reproduction report

Generated 2026-10-30 18:35 from 72 cached runs.

## Thesis claims

| ID | Claim | Source | Status | Measured |
|---|---|---|---|---|
| C01 | Centralised PPO binary F1 is about 0.986 (tolerance 0.01) | Ch.4 Sec. 1-4-4 | REPRODUCED | F1=0.9845 |
| C02 | Federated clean F1 is within 0.01 of centralised PPO (thesis: 0.9842 vs 0.986) | Ch.4 Table 4-7 | REPRODUCED | federated F1=0.9886, centralised F1=0.9845 |
| C03 | Random forest scores at least the PPO F1 (thesis Table 4-18: 0.9990 vs 0.9860) | Ch.4 Table 4-18 | NOT RUN | not run: baseline/binary/rf, baseline/binary/ppo |
| C04 | Thesis profiles: legacy backup16 clean F1 is at least 0.98 (thesis: 0.9842) | Ch.4 Table 4-7; backup16 code | NOT RUN | not run: profile/legacy_backup16/clean |
| C05 | Geometric median with F1 weighting keeps 98% of clean F1 under 60% model poisoning | Ch.4 Table 4-9 | REPRODUCED | clean=0.9886, attacked=0.9885, ratio=1.000 |
| C06 | Unweighted FedAvg collapses (F1 drop of at least 0.10) under 60% model poisoning | Ch.4 Table 4-24 | REPRODUCED | clean=0.9885, attacked=0.8555, drop=0.1330 |
| C07 | FedAvg with F1 weighting keeps 98% of clean F1 under 60% model poisoning | Ch.4 Table 4-23 (FedAvg + F1) | NOT REPRODUCED | clean=0.9890, attacked=0.8458, ratio=0.855 |
| C08 | F1 weighting, not the aggregation rule, decides robustness: GM+F1 within 0.01 of FedAvg+F1 | Ch.4 Table 4-23; Sec. 9-4 conclusion | NOT REPRODUCED | GM+F1=0.9885, FedAvg+F1=0.8458 |
| C09 | GM+F1 under 60% label flipping keeps F1 of about 0.9625 (tolerance 0.01) | Ch.4 Table 4-8 | NOT REPRODUCED | F1=0.9877 |
| C10 | Krum beats geometric median under 60% label flipping (thesis Table 4-22) | Ch.4 Table 4-22 | REPRODUCED | Krum F1=0.9839, GM F1=0.4111 |
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
| agg/clean/fedavg+f1 | 0.9890 | 0.0423 | 0.0067 | 0.9933 | 0.495 | 1271.36 |
| agg/clean/fedavg+none | 0.9885 | 0.0466 | 0.0061 | 0.9939 | 0.496 | 1276.29 |
| agg/clean/geometric_median+f1 | 0.9886 | 0.0455 | 0.0064 | 0.9936 | 0.506 | 1273.95 |
| agg/clean/geometric_median+none | 0.9888 | 0.0440 | 0.0064 | 0.9936 | 0.503 | 1268.73 |
| agg/clean/krum+none | 0.9861 | 0.0400 | 0.0132 | 0.9868 | 0.499 | 1270.47 |
| agg/clean/median+none | 0.9886 | 0.0447 | 0.0067 | 0.9933 | 0.500 | 1270.23 |
| agg/clean/multi_krum+none | 0.9888 | 0.0444 | 0.0062 | 0.9938 | 0.502 | 1272.1 |
| agg/clean/trimmed_mean+none | 0.9890 | 0.0431 | 0.0064 | 0.9936 | 0.500 | 1266.91 |
| baseline/binary/ppo | 0.9845 | 0.0608 | 0.0090 | 0.9910 | 0.493 | 130.69 |
| defense/clean/gate | 0.9592 | 0.2029 | 0.0102 | 0.9898 | 0.492 | 1378.56 |
| defense/clean/gate+zscore | 0.9592 | 0.2029 | 0.0102 | 0.9898 | 0.492 | 1395.79 |
| defense/clean/gate+zscore+exclusion | 0.9592 | 0.2029 | 0.0102 | 0.9898 | 0.492 | 1406.29 |
| defense/clean/none | 0.9592 | 0.2029 | 0.0102 | 0.9898 | 0.492 | 1382.21 |
| defense/model_noise/gate | 0.9631 | 0.1597 | 0.0171 | 0.9829 | 0.494 | 1380.29 |
| defense/model_noise/gate+zscore | 0.9631 | 0.1597 | 0.0171 | 0.9829 | 0.494 | 1402.98 |
| defense/model_noise/none | 0.9674 | 0.1357 | 0.0166 | 0.9834 | 0.495 | 1388.03 |
| poison/clean/fedavg+f1 | 0.9890 | 0.0423 | 0.0067 | 0.9933 | 0.495 | 1266.38 |
| poison/clean/fedavg+none | 0.9885 | 0.0466 | 0.0061 | 0.9939 | 0.496 | 1270.93 |
| poison/clean/geometric_median+f1 | 0.9886 | 0.0455 | 0.0064 | 0.9936 | 0.506 | 1280.65 |
| poison/clean/geometric_median+none | 0.9888 | 0.0440 | 0.0064 | 0.9936 | 0.503 | 1275.25 |
| poison/clean/krum+none | 0.9861 | 0.0400 | 0.0132 | 0.9868 | 0.499 | 1262.14 |
| poison/clean/median+none | 0.9886 | 0.0447 | 0.0067 | 0.9933 | 0.500 | 1264.86 |
| poison/clean/multi_krum+none | 0.9888 | 0.0444 | 0.0062 | 0.9938 | 0.502 | 1271.16 |
| poison/clean/trimmed_mean+none | 0.9890 | 0.0431 | 0.0064 | 0.9936 | 0.500 | 1265.65 |
| poison/label_flip/20/fedavg+f1 | 0.9885 | 0.0465 | 0.0061 | 0.9939 | 0.496 | 1263.21 |
| poison/label_flip/20/fedavg+none | 0.9883 | 0.0481 | 0.0061 | 0.9939 | 0.502 | 1270.28 |
| poison/label_flip/20/geometric_median+f1 | 0.9884 | 0.0470 | 0.0062 | 0.9938 | 0.497 | 1281.0 |
| poison/label_flip/20/geometric_median+none | 0.9882 | 0.0462 | 0.0068 | 0.9932 | 0.495 | 1279.95 |
| poison/label_flip/20/krum+none | 0.9790 | 0.0444 | 0.0257 | 0.9743 | 0.510 | 1292.24 |
| poison/label_flip/20/median+none | 0.9887 | 0.0444 | 0.0066 | 0.9934 | 0.493 | 1285.9 |
| poison/label_flip/20/multi_krum+none | 0.9885 | 0.0470 | 0.0060 | 0.9940 | 0.494 | 1299.01 |
| poison/label_flip/20/trimmed_mean+none | 0.9883 | 0.0437 | 0.0075 | 0.9925 | 0.493 | 1289.59 |
| poison/label_flip/40/fedavg+f1 | 0.9885 | 0.0452 | 0.0066 | 0.9934 | 0.486 | 1278.75 |
| poison/label_flip/40/fedavg+none | 0.9878 | 0.0483 | 0.0069 | 0.9931 | 0.494 | 1280.05 |
| poison/label_flip/40/geometric_median+f1 | 0.9883 | 0.0465 | 0.0066 | 0.9934 | 0.495 | 1281.66 |
| poison/label_flip/40/geometric_median+none | 0.9881 | 0.0454 | 0.0073 | 0.9927 | 0.485 | 1277.39 |
| poison/label_flip/40/krum+none | 0.9860 | 0.0427 | 0.0124 | 0.9876 | 0.488 | 1275.59 |
| poison/label_flip/40/median+none | 0.9886 | 0.0452 | 0.0065 | 0.9935 | 0.487 | 1289.99 |
| poison/label_flip/40/multi_krum+none | 0.9886 | 0.0451 | 0.0065 | 0.9935 | 0.483 | 1275.14 |
| poison/label_flip/40/trimmed_mean+none | 0.9878 | 0.0456 | 0.0078 | 0.9922 | 0.489 | 1289.6 |
| poison/label_flip/60/fedavg+f1 | 0.9886 | 0.0426 | 0.0074 | 0.9926 | 0.492 | 1297.36 |
| poison/label_flip/60/fedavg+none | 0.4377 | 0.0109 | 0.7187 | 0.2813 | 0.506 | 1295.62 |
| poison/label_flip/60/geometric_median+f1 | 0.9877 | 0.0450 | 0.0084 | 0.9916 | 0.498 | 1294.62 |
| poison/label_flip/60/geometric_median+none | 0.4111 | 0.0234 | 0.7391 | 0.2609 | 0.505 | 1302.41 |
| poison/label_flip/60/krum+none | 0.9839 | 0.0580 | 0.0112 | 0.9888 | 0.492 | 1304.54 |
| poison/label_flip/60/median+none | 0.3224 | 0.0102 | 0.8071 | 0.1929 | 0.506 | 1304.01 |
| poison/label_flip/60/multi_krum+none | 0.9884 | 0.0439 | 0.0072 | 0.9928 | 0.504 | 1297.78 |
| poison/label_flip/60/trimmed_mean+none | 0.3629 | 0.0134 | 0.7773 | 0.2227 | 0.504 | 1304.57 |
| poison/model_noise/20/fedavg+f1 | 0.8460 | 0.9969 | 0.0001 | 0.9999 | 0.492 | 1301.92 |
| poison/model_noise/20/fedavg+none | 0.8179 | 0.8166 | 0.1018 | 0.8982 | 0.493 | 1308.05 |
| poison/model_noise/20/geometric_median+f1 | 0.9886 | 0.0452 | 0.0063 | 0.9937 | 0.511 | 1307.36 |
| poison/model_noise/20/geometric_median+none | 0.9891 | 0.0423 | 0.0065 | 0.9935 | 0.501 | 1304.29 |
| poison/model_noise/20/krum+none | 0.9868 | 0.0507 | 0.0080 | 0.9920 | 0.502 | 1312.43 |
| poison/model_noise/20/median+none | 0.9889 | 0.0424 | 0.0069 | 0.9931 | 0.506 | 1331.66 |
| poison/model_noise/20/multi_krum+none | 0.9887 | 0.0450 | 0.0063 | 0.9937 | 0.497 | 1326.2 |
| poison/model_noise/20/trimmed_mean+none | 0.3728 | 0.5682 | 0.7234 | 0.2766 | 0.496 | 1350.18 |
| poison/model_noise/40/fedavg+f1 | 0.8554 | 0.9207 | 0.0014 | 0.9986 | 0.496 | 1316.17 |
| poison/model_noise/40/fedavg+none | 0.7313 | 0.5603 | 0.3057 | 0.6943 | 0.507 | 1302.06 |
| poison/model_noise/40/geometric_median+f1 | 0.9885 | 0.0440 | 0.0070 | 0.9930 | 0.508 | 1302.64 |
| poison/model_noise/40/geometric_median+none | 0.9884 | 0.0460 | 0.0065 | 0.9935 | 0.504 | 1295.89 |
| poison/model_noise/40/krum+none | 0.9808 | 0.0718 | 0.0125 | 0.9875 | 0.500 | 1294.36 |
| poison/model_noise/40/median+none | 0.9887 | 0.0422 | 0.0072 | 0.9928 | 0.506 | 1320.62 |
| poison/model_noise/40/multi_krum+none | 0.9886 | 0.0451 | 0.0065 | 0.9935 | 0.503 | 1316.79 |
| poison/model_noise/40/trimmed_mean+none | 0.7203 | 0.4800 | 0.3386 | 0.6614 | 0.506 | 1340.46 |
| poison/model_noise/60/fedavg+f1 | 0.8458 | 0.9991 | 0.0000 | 1.0000 | 0.493 | 1334.66 |
| poison/model_noise/60/fedavg+none | 0.8555 | 0.9062 | 0.0053 | 0.9947 | 0.497 | 1324.77 |
| poison/model_noise/60/geometric_median+f1 | 0.9885 | 0.0392 | 0.0088 | 0.9912 | 0.508 | 1355.85 |
| poison/model_noise/60/geometric_median+none | 0.9886 | 0.0436 | 0.0069 | 0.9931 | 0.502 | 1356.79 |
| poison/model_noise/60/krum+none | 0.9860 | 0.0507 | 0.0095 | 0.9905 | 0.511 | 1349.13 |
| poison/model_noise/60/median+none | 0.4713 | 0.5147 | 0.6338 | 0.3662 | 0.502 | 1382.25 |
| poison/model_noise/60/multi_krum+none | 0.9883 | 0.0461 | 0.0068 | 0.9932 | 0.500 | 1354.81 |
| poison/model_noise/60/trimmed_mean+none | 0.8410 | 0.8971 | 0.0368 | 0.9632 | 0.496 | 1381.88 |
