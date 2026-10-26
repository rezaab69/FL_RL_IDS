"""Command line interface.

    python -m fl_ids list                         list suites, profiles and budgets
    python -m fl_ids run SUITE [--budget B] [--only REGEX] [--force]
    python -m fl_ids report                       write reports/report.md
    python -m fl_ids data                         check the dataset and print class counts
    python -m fl_ids test                         run the unit tests (pytest)
"""
from __future__ import annotations

import argparse
import subprocess
import sys

from .scenarios import BUDGETS, PROFILES, SUITE_BUILDERS, build_suite


def cmd_list(_args):
    print("Suites:  " + ", ".join(sorted(SUITE_BUILDERS)) + ", all")
    print("Budgets: " + ", ".join(BUDGETS))
    print("Profiles: " + ", ".join(PROFILES))


def cmd_run(args):
    from .runner import run_configs
    configs = build_suite(args.suite, args.budget)
    print(f"{len(configs)} configurations in suite '{args.suite}' at budget '{args.budget}'")
    records = run_configs(configs, force=args.force, only=args.only)
    failed = [r for r in records if "error" in r]
    print(f"done: {len(records) - len(failed)} ok, {len(failed)} failed")
    for r in failed:
        print(f"  {r['name']}: {r['error']}")


def cmd_report(_args):
    from .report import build_report
    print("report written to " + build_report())


def cmd_data(_args):
    import numpy as np
    from .config import DataConfig
    from .data import build_dataset
    ds = build_dataset(DataConfig())
    print(f"train {ds.X_train.shape}, test {ds.X_test.shape}, features {ds.n_features}, task {ds.task}")
    names, counts = np.unique(ds.test_raw, return_counts=True)
    for n, c in zip(names, counts):
        print(f"  test rows {n}: {c}")


def cmd_test(_args):
    sys.exit(subprocess.call([sys.executable, "-m", "pytest", "-q", "tests"]))


def main(argv=None):
    p = argparse.ArgumentParser(prog="fl_ids")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("list").set_defaults(func=cmd_list)
    r = sub.add_parser("run")
    r.add_argument("suite")
    r.add_argument("--budget", default="quick", choices=list(BUDGETS))
    r.add_argument("--only", default=None, help="regex on configuration names")
    r.add_argument("--force", action="store_true", help="ignore cached results")
    r.set_defaults(func=cmd_run)
    sub.add_parser("report").set_defaults(func=cmd_report)
    sub.add_parser("data").set_defaults(func=cmd_data)
    sub.add_parser("test").set_defaults(func=cmd_test)
    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
