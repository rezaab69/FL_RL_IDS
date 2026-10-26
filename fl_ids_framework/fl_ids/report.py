"""Markdown report: thesis-claim verdicts, every cached run, zero-day table and aggregation timings."""
from __future__ import annotations

import os
import time

from .claims import evaluate
from .runner import FRAMEWORK_DIR, load_results


def _fmt(v, digits=4):
    return "" if v is None else f"{v:.{digits}f}"


def build_report(out_path: str | None = None) -> str:
    R = load_results()
    lines = [
        "# Thesis reproduction report",
        "",
        f"Generated {time.strftime('%Y-%m-%d %H:%M')} from {len(R)} cached runs.",
        "",
        "## Thesis claims",
        "",
        "| ID | Claim | Source | Status | Measured |",
        "|---|---|---|---|---|",
    ]
    for row in evaluate(R):
        lines.append(f"| {row['id']} | {row['claim']} | {row['source']} | {row['status']} | {row['measured']} |")

    lines += ["", "## Runs", "", "| Run | F1 | FPR | FNR | Recall | MIA AUC | Seconds |",
              "|---|---|---|---|---|---|---|"]
    for name in sorted(R):
        rec = R[name]
        res = rec["result"]
        if "final" not in res:
            lines.append(f"| {name} | | | | | | {rec.get('seconds', '')} |")
            continue
        f = res["final"]
        lines.append(f"| {name} | {_fmt(f.get('f1'))} | {_fmt(f.get('fpr'))} | {_fmt(f.get('fnr'))} | "
                     f"{_fmt(f.get('recall'))} | {_fmt(f.get('mia_auc'), 3)} | {rec.get('seconds', '')} |")

    zero = sorted(n for n in R if n.startswith("zeroday/"))
    if zero:
        lines += ["", "## Zero-day detection (held-out class detection rate)", "",
                  "| Held-out class | Model | Detection | FPR |", "|---|---|---|---|"]
        for name in zero:
            _, cls, model = name.split("/", 2)
            f = R[name]["result"]["final"]
            lines.append(f"| {cls} | {model} | {_fmt(f['per_class_detection'].get(cls))} | {_fmt(f.get('fpr'))} |")

    for name in sorted(n for n in R if n.startswith("scaling/") or n.endswith("bench")):
        rows = R[name]["result"].get("rows", [])
        if not rows:
            continue
        lines += ["", f"## Aggregation timing: {name}", "",
                  "| Params | Clients | Aggregator | Median seconds |", "|---|---|---|---|"]
        for r in rows:
            lines.append(f"| {r['n_params']} | {r['n_clients']} | {r['aggregator']} | {r['median_seconds']:.6f} |")

    text = "\n".join(lines) + "\n"
    out_path = out_path or os.path.join(FRAMEWORK_DIR, "reports", "report.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return out_path
