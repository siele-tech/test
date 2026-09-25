from pathlib import Path

import pandas as pd
import pytest

from sales_pipeline.validate import validate_files, validate_frame

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def good_rows() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["ORD-1", "ORD-2", "ORD-3"],
            "order_date": ["2026-09-25"] * 3,
            "customer_id": ["C1001", "C1002", "C1003"],
            "product": ["Yoga Mat", "Smart Watch", "Desk Lamp"],
            "category": ["Sports", "Electronics", "Office"],
            "region": ["North", "East", "West"],
            "quantity": [1, 2, 1],
            "unit_price": [24.99, 149.00, 27.90],
        }
    )


def test_clean_data_passes():
    assert validate_frame(good_rows()) == []


@pytest.mark.parametrize(
    ("column", "bad_value", "expected"),
    [
        ("unit_price", -10.0, "unit_price must be positive"),
        ("unit_price", 99999.0, "likely typo"),
        ("unit_price", "abc", "unit_price is not a number"),
        ("quantity", 0, "quantity must be a whole number"),
        ("quantity", 1.5, "quantity must be a whole number"),
        ("quantity", "two", "quantity is not a number"),
        ("region", "Atlantis", "unknown region"),
        ("order_date", "25/09/2026", "invalid order_date"),
        ("customer_id", None, "missing values"),
    ],
)
def test_bad_values_are_caught(column, bad_value, expected):
    df = good_rows()
    df[column] = df[column].astype(object)
    df.loc[1, column] = bad_value
    errors = validate_frame(df)
    assert any(expected in e for e in errors), errors


def test_duplicate_order_ids_are_caught():
    df = good_rows()
    df.loc[2, "order_id"] = "ORD-1"
    assert any("duplicate order_id" in e for e in validate_frame(df))


def test_missing_column_is_caught():
    df = good_rows().drop(columns=["unit_price"])
    assert any("missing columns" in e for e in validate_frame(df))


def test_error_reports_the_csv_line_number():
    df = good_rows()
    df.loc[1, "unit_price"] = -5.0  # second data row = line 3 of the CSV
    assert any("line 3" in e for e in validate_frame(df))


def test_order_dated_on_wrong_day_is_caught(tmp_path):
    df = good_rows()
    df.loc[0, "order_date"] = "2026-09-24"
    path = tmp_path / "2026-09-25.csv"
    df.to_csv(path, index=False)
    assert any("dated outside" in e for e in validate_files([path]))


def test_same_orders_in_two_files_is_caught(tmp_path):
    good_rows().to_csv(tmp_path / "2026-09-25.csv", index=False)
    good_rows().assign(order_date="2026-09-26").to_csv(tmp_path / "2026-09-26.csv", index=False)
    errors = validate_files(sorted(tmp_path.glob("*.csv")))
    assert any("more than one file" in e for e in errors)


def test_committed_data_is_clean():
    """Everything in data/raw must always pass the gate."""
    paths = sorted((DATA_DIR / "raw").glob("*.csv"))
    assert paths, "no data files found"
    assert validate_files(paths) == []


def test_bad_sample_is_rejected():
    """The demo file in data/samples must keep failing, so the demo stays reliable."""
    errors = validate_files(sorted((DATA_DIR / "samples").glob("*.csv")))
    assert len(errors) >= 5
