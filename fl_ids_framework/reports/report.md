# Thesis reproduction report

Generated 2026-10-31 11:39 from 150 cached runs.

## Thesis claims

| ID | Claim | Source | Status | Measured |
|---|---|---|---|---|
| C01 | Centralised PPO binary F1 is about 0.986 (tolerance 0.01) | Ch.4 Sec. 1-4-4 | REPRODUCED | F1=0.9845 |
| C02 | Federated clean F1 is within 0.01 of centralised PPO (thesis: 0.9842 vs 0.986) | Ch.4 Table 4-7 | REPRODUCED | federated F1=0.9886, centralised F1=0.9845 |
| C03 | Random forest scores at least the PPO F1 (thesis Table 4-18: 0.9990 vs 0.9860) | Ch.4 Table 4-18 | REPRODUCED | RF F1=0.9983, PPO F1=0.9845 |
| C04 | Thesis profiles: legacy backup16 clean F1 is at least 0.98 (thesis: 0.9842) | Ch.4 Table 4-7; backup16 code | REPRODUCED | F1=0.9882 |
| C05 | Geometric median with F1 weighting keeps 98% of clean F1 under 60% model poisoning | Ch.4 Table 4-9 | REPRODUCED | clean=0.9886, attacked=0.9885, ratio=1.000 |
| C06 | Unweighted FedAvg collapses (F1 drop of at least 0.10) under 60% model poisoning | Ch.4 Table 4-24 | REPRODUCED | clean=0.9885, attacked=0.8555, drop=0.1330 |
| C07 | FedAvg with F1 weighting keeps 98% of clean F1 under 60% model poisoning | Ch.4 Table 4-23 (FedAvg + F1) | NOT REPRODUCED | clean=0.9890, attacked=0.8458, ratio=0.855 |
| C08 | F1 weighting, not the aggregation rule, decides robustness: GM+F1 within 0.01 of FedAvg+F1 | Ch.4 Table 4-23; Sec. 9-4 conclusion | NOT REPRODUCED | GM+F1=0.9885, FedAvg+F1=0.8458 |
| C09 | GM+F1 under 60% label flipping keeps F1 of about 0.9625 (tolerance 0.01) | Ch.4 Table 4-8 | NOT REPRODUCED | F1=0.9877 |
| C10 | Krum beats geometric median under 60% label flipping (thesis Table 4-22) | Ch.4 Table 4-22 | REPRODUCED | Krum F1=0.9839, GM F1=0.4111 |
| C11 | Defence stack (gate + Z-score + exclusion) keeps 98% of clean F1 under 40% model poisoning | Ch.3 Sec. 7-3; Ch.4 Sec. 5-4 | REPRODUCED | clean=0.9592, attacked=0.9631, ratio=1.004 |
| C12 | Differential privacy at epsilon 8 (update target, C=1) keeps 98% of the no-DP F1 | Ch.3 Algorithm 4 | NOT REPRODUCED | no DP=0.9886, eps=8=0.1731 |
| C13 | Thesis-literal DP (noise on parameters, epsilon 1) keeps 98% of the no-DP F1 | Ch.3 Algorithm 4 (literal) | NOT REPRODUCED | no DP=0.9886, literal eps=1=0.1705 |
| C14 | H3 privacy direction: federated model leaks less membership signal than centralised PPO | Ch.1 hypothesis 3 | NOT REPRODUCED | federated MIA AUC=0.506, centralised MIA AUC=0.493 |
| C15 | PPO detects held-out Port Scan at 95% or more (thesis: 97.72%) | Ch.4 Table 4-11 | REPRODUCED | detection=0.9753 |
| C16 | PPO detects held-out ICMP Flood at 5% or less (thesis: about 0%) | Ch.4 Table 4-12 | REPRODUCED | detection=0.0000 |
| C17 | H1: PPO detects held-out attacks at least as well as random forest on average | Ch.4 Sec. 6-4 and Table 4-27 | REPRODUCED | mean PPO detection=0.4295, mean RF detection=0.2078 over 11 classes |
| C18 | Geometric median overhead vs FedAvg at 100 clients is at most 12.4x (thesis Table 4-16) | Ch.4 Table 4-16 | NOT REPRODUCED | GM=49.76 ms, FedAvg=1.13 ms, ratio=44.0x |
| C19 | Geometric median time grows at most 20x from 5 to 100 clients (thesis: near-linear) | Ch.4 Table 4-14 | NOT REPRODUCED | 5 clients=1.92 ms, 100 clients=49.76 ms |
| C20 | PPO hyper-parameter choice barely changes federated F1 (thesis_table44 vs thesis_spec, 0.01) | Ch.3 Sec. 3-3-3 vs Ch.4 Table 4-4 | NOT REPRODUCED | thesis_spec=0.9592, thesis_table44=0.9884 |

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
| baseline/binary/dqn | 0.9881 | 0.0538 | 0.0044 | 0.9956 | 0.504 | 768.52 |
| baseline/binary/dt | 0.9979 | 0.0072 | 0.0015 | 0.9985 | 0.502 | 36.56 |
| baseline/binary/ppo | 0.9845 | 0.0608 | 0.0090 | 0.9910 | 0.493 | 130.69 |
| baseline/binary/rf | 0.9983 | 0.0064 | 0.0010 | 0.9990 | 0.500 | 160.9 |
| baseline/binary/xgb | 0.9979 | 0.0097 | 0.0006 | 0.9994 | 0.510 | 73.82 |
| baseline/multiclass/dt | 0.9979 | 0.0073 | 0.0015 | 0.9985 | 0.498 | 34.32 |
| baseline/multiclass/rf | 0.9983 | 0.0065 | 0.0011 | 0.9989 | 0.501 | 186.76 |
| baseline/multiclass/xgb | 0.9979 | 0.0101 | 0.0006 | 0.9994 | 0.507 | 531.52 |
| defense/clean/gate | 0.9592 | 0.2029 | 0.0102 | 0.9898 | 0.492 | 1378.56 |
| defense/clean/gate+zscore | 0.9592 | 0.2029 | 0.0102 | 0.9898 | 0.492 | 1395.79 |
| defense/clean/gate+zscore+exclusion | 0.9592 | 0.2029 | 0.0102 | 0.9898 | 0.492 | 2702.66 |
| defense/clean/none | 0.9592 | 0.2029 | 0.0102 | 0.9898 | 0.492 | 1382.21 |
| defense/model_noise/gate | 0.9631 | 0.1597 | 0.0171 | 0.9829 | 0.494 | 1380.29 |
| defense/model_noise/gate+zscore | 0.9631 | 0.1597 | 0.0171 | 0.9829 | 0.494 | 1402.98 |
| defense/model_noise/gate+zscore+exclusion | 0.9631 | 0.1597 | 0.0171 | 0.9829 | 0.494 | 2656.94 |
| defense/model_noise/none | 0.9674 | 0.1357 | 0.0166 | 0.9834 | 0.495 | 1388.03 |
| dp/centralized_ppo | 0.9845 | 0.0608 | 0.0090 | 0.9910 | 0.493 | 257.42 |
| dp/nodp | 0.9886 | 0.0455 | 0.0064 | 0.9936 | 0.506 | 2737.56 |
| dp/parameters_eps1_literal | 0.1705 | 0.3306 | 0.8956 | 0.1044 | 0.508 | 2540.58 |
| dp/update_eps1_C0.1 | 0.1490 | 0.1569 | 0.9149 | 0.0851 | 0.510 | 2586.49 |
| dp/update_eps1_C1 | 0.1701 | 0.3147 | 0.8963 | 0.1037 | 0.508 | 2609.44 |
| dp/update_eps8_C1 | 0.1731 | 0.0515 | 0.9035 | 0.0965 | 0.508 | 2666.16 |
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
| profile/legacy_backup16/clean | 0.9882 | 0.0504 | 0.0053 | 0.9947 | 0.504 | 2731.63 |
| profile/legacy_backup16/model_noise60 | 0.9879 | 0.0442 | 0.0081 | 0.9919 | 0.507 | 2778.77 |
| profile/plain_fedavg/clean | 0.9889 | 0.0447 | 0.0060 | 0.9940 | 0.497 | 2790.85 |
| profile/plain_fedavg/model_noise60 | 0.0005 | 0.0055 | 0.9998 | 0.0002 | 0.507 | 2768.25 |
| profile/thesis_spec/clean | 0.9592 | 0.2029 | 0.0102 | 0.9898 | 0.492 | 2691.67 |
| profile/thesis_spec/model_noise60 | 0.9588 | 0.1741 | 0.0206 | 0.9794 | 0.496 | 2650.56 |
| profile/thesis_table44/clean | 0.9884 | 0.0442 | 0.0071 | 0.9929 | 0.506 | 2601.82 |
| profile/thesis_table44/model_noise60 | 0.9885 | 0.0440 | 0.0071 | 0.9929 | 0.497 | 2683.23 |
| scaling/bench | | | | | | 1.06 |
| zeroday/ARP Spoofing/dqn | 0.9898 | 0.0421 | 0.0051 | 0.9949 | 0.492 | 768.13 |
| zeroday/ARP Spoofing/dt | 0.9978 | 0.0075 | 0.0017 | 0.9983 | 0.503 | 36.45 |
| zeroday/ARP Spoofing/ppo | 0.9841 | 0.0544 | 0.0121 | 0.9879 | 0.498 | 289.37 |
| zeroday/ARP Spoofing/rf | 0.9982 | 0.0064 | 0.0013 | 0.9987 | 0.510 | 160.51 |
| zeroday/ARP Spoofing/xgb | 0.9979 | 0.0098 | 0.0006 | 0.9994 | 0.496 | 71.58 |
| zeroday/DNS Flood/dqn | 0.8711 | 0.0401 | 0.2190 | 0.7810 | 0.569 | 699.98 |
| zeroday/DNS Flood/dt | 0.8809 | 0.0067 | 0.2112 | 0.7888 | 0.580 | 32.22 |
| zeroday/DNS Flood/ppo | 0.8668 | 0.0660 | 0.2199 | 0.7801 | 0.586 | 286.58 |
| zeroday/DNS Flood/rf | 0.8793 | 0.0062 | 0.2139 | 0.7861 | 0.581 | 146.96 |
| zeroday/DNS Flood/xgb | 0.8783 | 0.0098 | 0.2147 | 0.7853 | 0.582 | 68.03 |
| zeroday/Dictionary Attack/dqn | 0.9728 | 0.0456 | 0.0377 | 0.9623 | 0.516 | 721.3 |
| zeroday/Dictionary Attack/dt | 0.9804 | 0.0068 | 0.0361 | 0.9639 | 0.514 | 34.04 |
| zeroday/Dictionary Attack/ppo | 0.9668 | 0.0713 | 0.0406 | 0.9594 | 0.527 | 282.99 |
| zeroday/Dictionary Attack/rf | 0.9808 | 0.0063 | 0.0355 | 0.9645 | 0.507 | 155.86 |
| zeroday/Dictionary Attack/xgb | 0.9805 | 0.0097 | 0.0349 | 0.9651 | 0.514 | 84.09 |
| zeroday/ICMP Flood/dqn | 0.5402 | 0.0461 | 0.6269 | 0.3731 | 0.757 | 716.7 |
| zeroday/ICMP Flood/dt | 0.5446 | 0.0071 | 0.6253 | 0.3747 | 0.759 | 28.72 |
| zeroday/ICMP Flood/ppo | 0.5375 | 0.0559 | 0.6287 | 0.3713 | 0.759 | 283.7 |
| zeroday/ICMP Flood/rf | 0.5448 | 0.0064 | 0.6252 | 0.3748 | 0.765 | 104.29 |
| zeroday/ICMP Flood/xgb | 0.5449 | 0.0097 | 0.6249 | 0.3751 | 0.764 | 59.65 |
| zeroday/OS Scan/dqn | 0.9892 | 0.0402 | 0.0090 | 0.9910 | 0.553 | 732.09 |
| zeroday/OS Scan/dt | 0.9945 | 0.0071 | 0.0088 | 0.9912 | 0.504 | 35.89 |
| zeroday/OS Scan/ppo | 0.9792 | 0.0411 | 0.0284 | 0.9716 | 0.541 | 290.16 |
| zeroday/OS Scan/rf | 0.9358 | 0.0063 | 0.1189 | 0.8811 | 0.567 | 152.85 |
| zeroday/OS Scan/xgb | 0.9870 | 0.0101 | 0.0225 | 0.9775 | 0.565 | 78.34 |
| zeroday/Ping Sweep/dqn | 0.8136 | 0.0210 | 0.3102 | 0.6898 | 0.622 | 700.28 |
| zeroday/Ping Sweep/dt | 0.8213 | 0.0023 | 0.3027 | 0.6973 | 0.614 | 36.05 |
| zeroday/Ping Sweep/ppo | 0.9867 | 0.0682 | 0.0078 | 0.9922 | 0.489 | 261.56 |
| zeroday/Ping Sweep/rf | 0.8215 | 0.0012 | 0.3026 | 0.6974 | 0.610 | 139.57 |
| zeroday/Ping Sweep/xgb | 0.8216 | 0.0012 | 0.3025 | 0.6975 | 0.616 | 70.07 |
| zeroday/Port Scan/dqn | 0.9895 | 0.0237 | 0.0180 | 0.9820 | 0.676 | 748.23 |
| zeroday/Port Scan/dt | 0.3676 | 0.0061 | 0.7746 | 0.2254 | 0.844 | 31.88 |
| zeroday/Port Scan/ppo | 0.9849 | 0.0372 | 0.0252 | 0.9748 | 0.582 | 277.74 |
| zeroday/Port Scan/rf | 0.9903 | 0.0058 | 0.0184 | 0.9816 | 0.864 | 108.36 |
| zeroday/Port Scan/xgb | 0.2962 | 0.0091 | 0.8260 | 0.1740 | 0.866 | 46.29 |
| zeroday/SYN Flood/dqn | 0.9553 | 0.0268 | 0.0772 | 0.9228 | 0.514 | 733.16 |
| zeroday/SYN Flood/dt | 0.9604 | 0.0070 | 0.0739 | 0.9261 | 0.524 | 35.55 |
| zeroday/SYN Flood/ppo | 0.9506 | 0.0312 | 0.0844 | 0.9156 | 0.505 | 277.11 |
| zeroday/SYN Flood/rf | 0.9608 | 0.0065 | 0.0734 | 0.9266 | 0.524 | 149.24 |
| zeroday/SYN Flood/xgb | 0.9605 | 0.0100 | 0.0728 | 0.9272 | 0.518 | 75.99 |
| zeroday/Slowloris/dqn | 0.9546 | 0.0413 | 0.0741 | 0.9259 | 0.536 | 731.03 |
| zeroday/Slowloris/dt | 0.9606 | 0.0072 | 0.0736 | 0.9264 | 0.525 | 35.08 |
| zeroday/Slowloris/ppo | 0.9630 | 0.0543 | 0.0543 | 0.9457 | 0.520 | 287.87 |
| zeroday/Slowloris/rf | 0.9490 | 0.0065 | 0.0951 | 0.9049 | 0.540 | 150.38 |
| zeroday/Slowloris/xgb | 0.9493 | 0.0098 | 0.0936 | 0.9064 | 0.538 | 72.34 |
| zeroday/UDP Flood/dqn | 0.9876 | 0.0436 | 0.0089 | 0.9911 | 0.517 | 764.27 |
| zeroday/UDP Flood/dt | 0.9959 | 0.0068 | 0.0057 | 0.9943 | 0.502 | 34.68 |
| zeroday/UDP Flood/ppo | 0.9602 | 0.0473 | 0.0607 | 0.9393 | 0.502 | 280.3 |
| zeroday/UDP Flood/rf | 0.9962 | 0.0062 | 0.0054 | 0.9946 | 0.494 | 160.61 |
| zeroday/UDP Flood/xgb | 0.9958 | 0.0097 | 0.0048 | 0.9952 | 0.506 | 74.49 |
| zeroday/Vulnerability Scan/dqn | 0.9885 | 0.0447 | 0.0092 | 0.9908 | 0.468 | 737.63 |
| zeroday/Vulnerability Scan/dt | 0.9927 | 0.0071 | 0.0124 | 0.9876 | 0.502 | 35.97 |
| zeroday/Vulnerability Scan/ppo | 0.9834 | 0.0503 | 0.0176 | 0.9824 | 0.512 | 267.66 |
| zeroday/Vulnerability Scan/rf | 0.9929 | 0.0064 | 0.0121 | 0.9879 | 0.580 | 144.55 |
| zeroday/Vulnerability Scan/xgb | 0.9936 | 0.0099 | 0.0096 | 0.9904 | 0.552 | 72.23 |

## Zero-day detection (held-out class detection rate)

| Held-out class | Model | Detection | FPR |
|---|---|---|---|
| ARP Spoofing | dqn | 0.0000 | 0.0421 |
| ARP Spoofing | dt | 0.0000 | 0.0075 |
| ARP Spoofing | ppo | 0.2000 | 0.0544 |
| ARP Spoofing | rf | 0.0000 | 0.0064 |
| ARP Spoofing | xgb | 0.0000 | 0.0098 |
| DNS Flood | dqn | 0.0003 | 0.0401 |
| DNS Flood | dt | 0.0252 | 0.0067 |
| DNS Flood | ppo | 0.0000 | 0.0660 |
| DNS Flood | rf | 0.0109 | 0.0062 |
| DNS Flood | xgb | 0.0051 | 0.0098 |
| Dictionary Attack | dqn | 0.0136 | 0.0456 |
| Dictionary Attack | dt | 0.0000 | 0.0068 |
| Dictionary Attack | ppo | 0.0983 | 0.0713 |
| Dictionary Attack | rf | 0.0000 | 0.0063 |
| Dictionary Attack | xgb | 0.0000 | 0.0097 |
| ICMP Flood | dqn | 0.0000 | 0.0461 |
| ICMP Flood | dt | 0.0001 | 0.0071 |
| ICMP Flood | ppo | 0.0000 | 0.0559 |
| ICMP Flood | rf | 0.0000 | 0.0064 |
| ICMP Flood | xgb | 0.0000 | 0.0097 |
| OS Scan | dqn | 0.9773 | 0.0402 |
| OS Scan | dt | 0.9581 | 0.0071 |
| OS Scan | ppo | 0.9711 | 0.0411 |
| OS Scan | rf | 0.3386 | 0.0063 |
| OS Scan | xgb | 0.8764 | 0.0101 |
| Ping Sweep | dqn | 0.0269 | 0.0210 |
| Ping Sweep | dt | 0.0001 | 0.0023 |
| Ping Sweep | ppo | 1.0000 | 0.0682 |
| Ping Sweep | rf | 0.0001 | 0.0012 |
| Ping Sweep | xgb | 0.0000 | 0.0012 |
| Port Scan | dqn | 0.9809 | 0.0237 |
| Port Scan | dt | 0.0640 | 0.0061 |
| Port Scan | ppo | 0.9753 | 0.0372 |
| Port Scan | rf | 0.9780 | 0.0058 |
| Port Scan | xgb | 0.0017 | 0.0091 |
| SYN Flood | dqn | 0.0000 | 0.0268 |
| SYN Flood | dt | 0.0001 | 0.0070 |
| SYN Flood | ppo | 0.0000 | 0.0312 |
| SYN Flood | rf | 0.0000 | 0.0065 |
| SYN Flood | xgb | 0.0000 | 0.0100 |
| Slowloris | dqn | 0.2665 | 0.0413 |
| Slowloris | dt | 0.2431 | 0.0072 |
| Slowloris | ppo | 0.5190 | 0.0543 |
| Slowloris | rf | 0.0146 | 0.0065 |
| Slowloris | xgb | 0.0255 | 0.0098 |
| UDP Flood | dqn | 0.0240 | 0.0436 |
| UDP Flood | dt | 0.0202 | 0.0068 |
| UDP Flood | ppo | 0.0063 | 0.0473 |
| UDP Flood | rf | 0.0038 | 0.0062 |
| UDP Flood | xgb | 0.0076 | 0.0097 |
| Vulnerability Scan | dqn | 0.9727 | 0.0447 |
| Vulnerability Scan | dt | 0.9403 | 0.0071 |
| Vulnerability Scan | ppo | 0.9542 | 0.0503 |
| Vulnerability Scan | rf | 0.9402 | 0.0064 |
| Vulnerability Scan | xgb | 0.9508 | 0.0099 |

## Aggregation timing: scaling/bench

| Params | Clients | Aggregator | Median seconds |
|---|---|---|---|
| 5410 | 5 | fedavg | 0.000017 |
| 5410 | 5 | geometric_median | 0.000889 |
| 5410 | 5 | krum | 0.000697 |
| 5410 | 5 | multi_krum | 0.000208 |
| 5410 | 5 | trimmed_mean | 0.000427 |
| 5410 | 5 | median | 0.000580 |
| 5410 | 10 | fedavg | 0.000016 |
| 5410 | 10 | geometric_median | 0.000721 |
| 5410 | 10 | krum | 0.000146 |
| 5410 | 10 | multi_krum | 0.000202 |
| 5410 | 10 | trimmed_mean | 0.000512 |
| 5410 | 10 | median | 0.001445 |
| 5410 | 50 | fedavg | 0.000065 |
| 5410 | 50 | geometric_median | 0.002144 |
| 5410 | 50 | krum | 0.000944 |
| 5410 | 50 | multi_krum | 0.001069 |
| 5410 | 50 | trimmed_mean | 0.001840 |
| 5410 | 50 | median | 0.005960 |
| 5410 | 100 | fedavg | 0.000138 |
| 5410 | 100 | geometric_median | 0.005841 |
| 5410 | 100 | krum | 0.002029 |
| 5410 | 100 | multi_krum | 0.003268 |
| 5410 | 100 | trimmed_mean | 0.004674 |
| 5410 | 100 | median | 0.011094 |
| 23330 | 5 | fedavg | 0.000046 |
| 23330 | 5 | geometric_median | 0.001924 |
| 23330 | 5 | krum | 0.000234 |
| 23330 | 5 | multi_krum | 0.000401 |
| 23330 | 5 | trimmed_mean | 0.001687 |
| 23330 | 5 | median | 0.002736 |
| 23330 | 10 | fedavg | 0.000098 |
| 23330 | 10 | geometric_median | 0.002124 |
| 23330 | 10 | krum | 0.000424 |
| 23330 | 10 | multi_krum | 0.000668 |
| 23330 | 10 | trimmed_mean | 0.002537 |
| 23330 | 10 | median | 0.006560 |
| 23330 | 50 | fedavg | 0.000433 |
| 23330 | 50 | geometric_median | 0.021363 |
| 23330 | 50 | krum | 0.003304 |
| 23330 | 50 | multi_krum | 0.005630 |
| 23330 | 50 | trimmed_mean | 0.014146 |
| 23330 | 50 | median | 0.029661 |
| 23330 | 100 | fedavg | 0.001131 |
| 23330 | 100 | geometric_median | 0.049755 |
| 23330 | 100 | krum | 0.009270 |
| 23330 | 100 | multi_krum | 0.015843 |
| 23330 | 100 | trimmed_mean | 0.030553 |
| 23330 | 100 | median | 0.061678 |
