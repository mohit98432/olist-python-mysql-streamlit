import pandas as pd
import pytest

from src.cleaning import clean_order_lines
from src.analysis import build_rfm, summarize


def sample_lines():
    return pd.DataFrame([
        {"order_id": 1, "customer_id": 1, "customer_unique_id": "a", "state": "SP", "order_date": "2025-01-01", "order_status": "delivered", "item_number": 1, "product_id": 1, "product_name": "A", "category": "books", "quantity": 2, "unit_price": 10.0, "discount_amount": None, "line_revenue": 0},
        {"order_id": 2, "customer_id": 1, "customer_unique_id": "a", "state": "SP", "order_date": "2025-02-01", "order_status": "delivered", "item_number": 1, "product_id": 1, "product_name": "A", "category": "books", "quantity": 1, "unit_price": 10.0, "discount_amount": 1.0, "line_revenue": 999},
        {"order_id": 3, "customer_id": 2, "customer_unique_id": "b", "state": "RJ", "order_date": "2025-02-03", "order_status": "delivered", "item_number": 1, "product_id": 2, "product_name": "B", "category": "toys", "quantity": -1, "unit_price": 5.0, "discount_amount": 0, "line_revenue": -5},
    ])


def test_cleaning_recomputes_money_drops_invalid():
    clean = clean_order_lines(sample_lines())
    assert len(clean) == 2
    assert clean.loc[0, "line_revenue"] == 20
    assert clean.loc[1, "line_revenue"] == 9
    assert str(clean.order_date.dtype).startswith("datetime64")


def test_summary_counts_orders_once_after_join():
    clean = clean_order_lines(sample_lines())
    metrics = summarize(clean)
    assert metrics["orders"] == 2
    assert metrics["customers"] == 1
    assert metrics["revenue"] == 29
    assert metrics["repeat_share"] == 1.0


def test_rfm_has_requested_metrics_and_segments():
    clean = clean_order_lines(sample_lines())
    result = build_rfm(clean)
    assert {"recency_days", "frequency_orders", "monetary_revenue", "segment"}.issubset(result.columns)
    assert len(result) == 1


def test_missing_required_column_fails_clearly():
    with pytest.raises(ValueError, match="Required column"):
        clean_order_lines(pd.DataFrame({"order_id": [1]}))
