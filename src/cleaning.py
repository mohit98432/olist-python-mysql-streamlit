"""Reusable, documented data quality steps for extracted order-line data."""
from __future__ import annotations

import pandas as pd

REQUIRED = ["order_id", "customer_unique_id", "order_date", "order_status", "category", "product_id", "quantity", "unit_price", "discount_amount", "line_revenue"]


def clean_order_lines(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize types, remove exact duplicate lines, and exclude invalid sales rows.

    Missing required identifiers or dates cannot be assigned to a business group,
    so those rows are excluded. Null discount is treated as zero per schema default.
    Negative quantities/prices and discounts exceeding gross line value are invalid.
    No statistical outlier rows are dropped: unusually large orders can be real.
    """
    df = frame.copy()
    if df.empty:
        return df
    for column in REQUIRED:
        if column not in df.columns:
            raise ValueError(f"Required column missing: {column}")
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    numeric = ["quantity", "unit_price", "discount_amount", "line_revenue"]
    for column in numeric:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df["discount_amount"] = df["discount_amount"].fillna(0)
    df = df.dropna(subset=["order_id", "customer_unique_id", "order_date", "category", "product_id"])
    df = df.drop_duplicates(subset=["order_id", "item_number"] if "item_number" in df else None)
    valid = (df["quantity"] > 0) & (df["unit_price"] >= 0) & (df["discount_amount"] >= 0)
    valid &= df["discount_amount"] <= df["quantity"] * df["unit_price"]
    df = df.loc[valid].copy()
    # Recompute revenue from trusted components to avoid stale or inconsistent totals.
    df["line_revenue"] = df["quantity"] * df["unit_price"] - df["discount_amount"]
    return df.reset_index(drop=True)
