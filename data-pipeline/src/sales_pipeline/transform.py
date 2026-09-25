"""Turn clean sales rows into the numbers the dashboard shows."""

from pathlib import Path

import pandas as pd


def load_sales(raw_dir: Path) -> pd.DataFrame:
    paths = sorted(raw_dir.glob("*.csv"))
    if not paths:
        raise FileNotFoundError(f"No CSV files found in {raw_dir}")
    df = pd.concat((pd.read_csv(p) for p in paths), ignore_index=True)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return add_revenue(df)


def add_revenue(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["revenue"] = df["quantity"] * df["unit_price"]
    return df


def pct_change(current: float, previous: float | None) -> float | None:
    if previous is None or previous == 0:
        return None
    return round((current - previous) / previous * 100, 2)


def daily_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("order_date")
        .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
        .reset_index()
        .sort_values("order_date")
    )


def latest_kpis(df: pd.DataFrame) -> dict:
    daily = daily_summary(df)
    today = daily.iloc[-1]
    prev = daily.iloc[-2] if len(daily) > 1 else None
    revenue = float(today["revenue"])
    orders = int(today["orders"])
    prev_aov = None if prev is None else float(prev["revenue"] / prev["orders"])
    aov = revenue / orders
    return {
        "date": today["order_date"].date().isoformat(),
        "revenue": round(revenue, 2),
        "orders": orders,
        "avgOrderValue": round(aov, 2),
        "revenueChangePct": pct_change(revenue, None if prev is None else float(prev["revenue"])),
        "ordersChangePct": pct_change(orders, None if prev is None else float(prev["orders"])),
        "avgOrderValueChangePct": pct_change(aov, prev_aov),
    }


def _ranked(df: pd.DataFrame, column: str, n: int | None = None) -> pd.DataFrame:
    ranked = (
        df.groupby(column, as_index=False)
        .agg(revenue=("revenue", "sum"), units=("quantity", "sum"))
        .sort_values("revenue", ascending=False)
    )
    return ranked.head(n) if n else ranked


def top_products(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    return _ranked(df, "product", n)


def revenue_by_region(df: pd.DataFrame) -> pd.DataFrame:
    return _ranked(df, "region")


def revenue_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return _ranked(df, "category")
