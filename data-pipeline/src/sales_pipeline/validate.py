"""Data-quality gate: bad sales data must never reach the dashboard."""

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "customer_id",
    "product",
    "category",
    "region",
    "quantity",
    "unit_price",
]
VALID_REGIONS = {"North", "South", "East", "West"}
MAX_UNIT_PRICE = 5_000  # anything above this is almost certainly a typo


def validate_frame(df: pd.DataFrame, source: str = "data") -> list[str]:
    """Return human-readable problems. An empty list means the data is clean."""
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        return [f"{source}: missing columns {missing_cols}"]

    errors: list[str] = []

    def report(mask: pd.Series, message: str) -> None:
        if mask.any():
            lines = (df.index[mask] + 2).tolist()  # +2: header row + 1-based lines
            shown = ", ".join(map(str, lines[:10])) + (" ..." if len(lines) > 10 else "")
            errors.append(f"{source}: {message} (line {shown})")

    report(df[REQUIRED_COLUMNS].isna().any(axis=1), "missing values")

    dates = pd.to_datetime(df["order_date"], format="%Y-%m-%d", errors="coerce")
    report(dates.isna() & df["order_date"].notna(), "invalid order_date")

    qty = pd.to_numeric(df["quantity"], errors="coerce")
    report(qty.isna() & df["quantity"].notna(), "quantity is not a number")
    report((qty < 1) | (qty % 1 != 0), "quantity must be a whole number >= 1")

    price = pd.to_numeric(df["unit_price"], errors="coerce")
    report(price.isna() & df["unit_price"].notna(), "unit_price is not a number")
    report(price <= 0, "unit_price must be positive")
    report(price > MAX_UNIT_PRICE, f"unit_price above {MAX_UNIT_PRICE} (likely typo)")

    report(~df["region"].isin(VALID_REGIONS) & df["region"].notna(), "unknown region")
    report(df["order_id"].duplicated(keep=False), "duplicate order_id")

    return errors


def validate_files(paths: list[Path]) -> list[str]:
    errors: list[str] = []
    frames = []
    for path in paths:
        df = pd.read_csv(path)
        errors += validate_frame(df, path.name)

        # A file named 2026-09-25.csv must only contain orders from that day.
        if "order_date" in df.columns:
            wrong_day = df["order_date"].astype(str) != path.stem
            if wrong_day.any():
                errors.append(f"{path.name}: {wrong_day.sum()} orders dated outside {path.stem}")
        frames.append(df.assign(_file=path.name))

    # Duplicates across files, e.g. the same day uploaded twice under another name.
    if frames:
        combined = pd.concat(frames, ignore_index=True)
        if "order_id" in combined.columns:
            per_id = combined.groupby("order_id")["_file"].nunique()
            cross = per_id[per_id > 1]
            if not cross.empty:
                errors.append(
                    f"{len(cross)} order_id(s) appear in more than one file, e.g. {cross.index[0]}"
                )
    return errors
