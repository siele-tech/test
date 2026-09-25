"""Export the dashboard data contract (JSON) consumed by the web app."""

import json
import os
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from sales_pipeline.transform import (
    daily_summary,
    latest_kpis,
    load_sales,
    revenue_by_category,
    revenue_by_region,
    top_products,
)

SCHEMA_VERSION = 1


def _records(df: pd.DataFrame, key: str) -> list[dict]:
    return [
        {"name": row[key], "revenue": round(float(row["revenue"]), 2), "units": int(row["units"])}
        for _, row in df.iterrows()
    ]


def build_payload(df: pd.DataFrame, files: int) -> dict:
    daily = daily_summary(df)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": datetime.now(UTC).isoformat(timespec="seconds"),
        "build": {
            "commit": os.getenv("GITHUB_SHA", "local")[:7],
            "runNumber": os.getenv("GITHUB_RUN_NUMBER"),
            "runUrl": (
                f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}"
                f"/actions/runs/{os.environ['GITHUB_RUN_ID']}"
                if os.getenv("GITHUB_RUN_ID")
                else None
            ),
        },
        "quality": {"status": "passed", "files": files, "rows": int(len(df))},
        "range": {
            "from": daily["order_date"].min().date().isoformat(),
            "to": daily["order_date"].max().date().isoformat(),
            "days": int(len(daily)),
        },
        "kpis": latest_kpis(df),
        "totals": {
            "revenue": round(float(df["revenue"].sum()), 2),
            "orders": int(df["order_id"].nunique()),
            "units": int(df["quantity"].sum()),
        },
        "daily": [
            {
                "date": row["order_date"].date().isoformat(),
                "revenue": round(float(row["revenue"]), 2),
                "orders": int(row["orders"]),
            }
            for _, row in daily.iterrows()
        ],
        "topProducts": _records(top_products(df), "product"),
        "regions": _records(revenue_by_region(df), "region"),
        "categories": _records(revenue_by_category(df), "category"),
    }


def export(raw_dir: Path, out: Path) -> dict:
    files = len(list(raw_dir.glob("*.csv")))
    payload = build_payload(load_sales(raw_dir), files)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
