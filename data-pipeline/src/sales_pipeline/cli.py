"""Command-line entry point.

    sales-pipeline validate [--raw-dir DIR]
    sales-pipeline export   [--raw-dir DIR] [--out FILE]
    sales-pipeline generate DATE [END_DATE] [--raw-dir DIR]

When running inside GitHub Actions, results are also written to the job
summary ($GITHUB_STEP_SUMMARY) so they show up on the run page.
"""

import argparse
import os
import sys
from datetime import date, timedelta
from pathlib import Path

from sales_pipeline.export import export
from sales_pipeline.generate import write_day
from sales_pipeline.validate import validate_files

DEFAULT_RAW = Path("data/raw")
DEFAULT_OUT = Path("../web/src/data/dashboard.json")


def _summary(markdown: str) -> None:
    path = os.getenv("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(markdown + "\n")


def cmd_validate(args: argparse.Namespace) -> int:
    paths = sorted(args.raw_dir.glob("*.csv"))
    if not paths:
        print(f"No CSV files found in {args.raw_dir}")
        return 1

    errors = validate_files(paths)
    if errors:
        print(f"DATA QUALITY CHECK FAILED - {len(errors)} problem(s):")
        for e in errors:
            print(f"  x {e}")
            # ::error:: makes each problem show up as an annotation on the run page
            print(f"::error title=Data quality::{e}")
        print("\nThe dashboard was NOT updated. Fix the data and push again.")
        _summary(
            "## ❌ Data quality check failed\n\n"
            + "\n".join(f"- {e}" for e in errors)
            + "\n\n**Deployment blocked** — the live dashboard still shows the last good data."
        )
        return 1

    print(f"Data quality check passed: {len(paths)} file(s) clean.")
    _summary(f"## ✅ Data quality check passed\n\n{len(paths)} daily sales files validated.")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    payload = export(args.raw_dir, args.out)
    k = payload["kpis"]
    rows, days = payload["quality"]["rows"], payload["range"]["days"]
    print(f"Exported {args.out} ({rows} rows, {days} days)")
    _summary(
        f"## 📊 Dashboard data exported\n\n"
        f"| Latest day | Revenue | Orders | Avg order value |\n|---|---|---|---|\n"
        f"| {k['date']} | ${k['revenue']:,.2f} | {k['orders']} | ${k['avgOrderValue']:,.2f} |"
    )
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    start = date.fromisoformat(args.date)
    end = date.fromisoformat(args.end_date) if args.end_date else start
    day = start
    while day <= end:
        print(f"wrote {write_day(day, args.raw_dir)}")
        day += timedelta(days=1)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sales-pipeline", description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="run the data-quality gate")
    p.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW)
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("export", help="export dashboard JSON for the web app")
    p.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("generate", help="generate sample sales for a date or date range")
    p.add_argument("date")
    p.add_argument("end_date", nargs="?")
    p.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW)
    p.set_defaults(func=cmd_generate)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
