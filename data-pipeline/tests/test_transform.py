import pandas as pd
import pytest

from sales_pipeline.transform import (
    add_revenue,
    daily_summary,
    latest_kpis,
    pct_change,
    revenue_by_category,
    revenue_by_region,
    top_products,
)


@pytest.fixture
def sales() -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "order_id": ["A", "B", "C", "D"],
            "order_date": pd.to_datetime(["2026-09-24", "2026-09-24", "2026-09-25", "2026-09-25"]),
            "product": ["Yoga Mat", "Smart Watch", "Smart Watch", "Desk Lamp"],
            "category": ["Sports", "Electronics", "Electronics", "Office"],
            "region": ["North", "North", "East", "West"],
            "quantity": [2, 1, 3, 1],
            "unit_price": [25.0, 150.0, 150.0, 30.0],
        }
    )
    return add_revenue(df)


def test_revenue_is_quantity_times_price(sales):
    assert sales["revenue"].tolist() == [50.0, 150.0, 450.0, 30.0]


def test_daily_summary(sales):
    daily = daily_summary(sales)
    assert daily["revenue"].tolist() == [200.0, 480.0]
    assert daily["orders"].tolist() == [2, 2]


def test_latest_kpis(sales):
    kpi = latest_kpis(sales)
    assert kpi["date"] == "2026-09-25"
    assert kpi["revenue"] == 480.0
    assert kpi["orders"] == 2
    assert kpi["avgOrderValue"] == 240.0
    assert kpi["revenueChangePct"] == pytest.approx(140.0)  # 200 -> 480
    assert kpi["ordersChangePct"] == pytest.approx(0.0)
    assert kpi["avgOrderValueChangePct"] == pytest.approx(140.0)  # 100 -> 240


def test_single_day_has_no_change(sales):
    one_day = sales[sales["order_date"] == "2026-09-25"]
    assert latest_kpis(one_day)["revenueChangePct"] is None


@pytest.mark.parametrize(
    ("current", "previous", "expected"),
    [(110, 100, 10.0), (90, 100, -10.0), (5, 0, None), (5, None, None)],
)
def test_pct_change(current, previous, expected):
    assert pct_change(current, previous) == expected


def test_top_products_ranked_by_revenue(sales):
    top = top_products(sales, n=2)
    assert top["product"].tolist() == ["Smart Watch", "Yoga Mat"]
    assert top["revenue"].tolist() == [600.0, 50.0]
    assert top["units"].tolist() == [4, 2]


def test_breakdowns_sum_to_total(sales):
    total = sales["revenue"].sum()
    assert revenue_by_region(sales)["revenue"].sum() == total
    assert revenue_by_category(sales)["revenue"].sum() == total
