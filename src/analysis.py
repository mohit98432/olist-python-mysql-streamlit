"""Pandas summaries and customer RFM segmentation."""
from __future__ import annotations

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def summarize(frame: pd.DataFrame) -> dict:
    """Return high-level metrics; orders are counted distinctly after line joins."""
    if frame.empty:
        return {"revenue": 0.0, "orders": 0, "customers": 0, "aov": 0.0, "repeat_share": 0.0}
    order_values = frame.groupby("order_id")["line_revenue"].sum()
    customer_orders = frame.groupby("customer_unique_id")["order_id"].nunique()
    return {
        "revenue": float(frame["line_revenue"].sum()),
        "orders": int(frame["order_id"].nunique()),
        "customers": int(frame["customer_unique_id"].nunique()),
        "aov": float(order_values.mean()) if len(order_values) else 0.0,
        "repeat_share": float((customer_orders > 1).mean()) if len(customer_orders) else 0.0,
    }


def build_rfm(frame: pd.DataFrame, as_of: pd.Timestamp | None = None, clusters: int = 4) -> pd.DataFrame:
    """Compute recency, frequency and monetary metrics, then K-Means segments.

    Features are standardized before K-Means so monetary scale does not dominate.
    Log transforms reduce skew. Labels are generic cluster IDs, not business truth.
    """
    cols = ["customer_unique_id", "recency_days", "frequency_orders", "monetary_revenue", "segment"]
    if frame.empty:
        return pd.DataFrame(columns=cols)
    ref = pd.Timestamp(as_of) if as_of is not None else pd.Timestamp(frame["order_date"].max()) + pd.DateOffset(days=1)
    rfm = frame.groupby("customer_unique_id").agg(
        last_purchase=("order_date", "max"),
        frequency_orders=("order_id", "nunique"),
        monetary_revenue=("line_revenue", "sum"),
    ).reset_index()
    rfm["recency_days"] = (ref - rfm["last_purchase"]).dt.days.clip(lower=0)
    features = rfm[["recency_days", "frequency_orders", "monetary_revenue"]].copy()
    features["recency_days"] = features["recency_days"].clip(lower=0)
    features = StandardScaler().fit_transform(np.log1p(features))
    k = max(1, min(int(clusters), len(rfm)))
    labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(features)
    rfm["segment"] = labels.astype(str)
    return rfm[cols].sort_values(["segment", "monetary_revenue"], ascending=[True, False]).reset_index(drop=True)
