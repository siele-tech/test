"""Generate a realistic day of sales for the demo store (deterministic per date)."""

import random
from datetime import date
from pathlib import Path

import pandas as pd

PRODUCTS: dict[str, tuple[str, float]] = {
    # product: (category, base unit price)
    "Wireless Earbuds": ("Electronics", 59.99),
    "Smart Watch": ("Electronics", 149.00),
    "USB-C Charger": ("Electronics", 19.99),
    "Laptop Stand": ("Office", 34.50),
    "Ergonomic Chair": ("Office", 219.00),
    "Desk Lamp": ("Office", 27.90),
    "Running Shoes": ("Sports", 89.00),
    "Yoga Mat": ("Sports", 24.99),
    "Water Bottle": ("Sports", 14.50),
    "Coffee Beans 1kg": ("Grocery", 18.75),
    "Green Tea Pack": ("Grocery", 9.99),
}
REGIONS = ["North", "South", "East", "West"]
REGION_WEIGHTS = [0.3, 0.2, 0.25, 0.25]


def generate_day(day: date) -> pd.DataFrame:
    rng = random.Random(day.toordinal())
    weekend_boost = 1.3 if day.weekday() >= 5 else 1.0
    trend = 1 + (day.toordinal() % 60) / 200
    n_orders = int(rng.randint(40, 70) * weekend_boost * trend)

    rows = []
    for i in range(1, n_orders + 1):
        product = rng.choice(list(PRODUCTS))
        category, base_price = PRODUCTS[product]
        rows.append(
            {
                "order_id": f"ORD-{day:%Y%m%d}-{i:04d}",
                "order_date": day.isoformat(),
                "customer_id": f"C{rng.randint(1000, 1999)}",
                "product": product,
                "category": category,
                "region": rng.choices(REGIONS, REGION_WEIGHTS)[0],
                "quantity": rng.choices([1, 2, 3, 4], [0.6, 0.25, 0.1, 0.05])[0],
                "unit_price": round(base_price * rng.uniform(0.9, 1.05), 2),
            }
        )
    return pd.DataFrame(rows)


def write_day(day: date, raw_dir: Path) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    out = raw_dir / f"{day.isoformat()}.csv"
    generate_day(day).to_csv(out, index=False, lineterminator="\n")
    return out
