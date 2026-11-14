"""Interactive Streamlit dashboard backed by live MySQL reads."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analysis import build_rfm, summarize
from src.cleaning import clean_order_lines
from src.db import get_engine, read_frame
from src.queries import ORDER_LINES

st.set_page_config(page_title="Olist Sales Analytics", page_icon="🛍️", layout="wide")
st.title("Olist Marketplace | Sales & Customer Analytics")
st.caption("Live MySQL data • Python + pandas • Synthetic portfolio dataset from the paired SQL project")

try:
    engine = get_engine()
    with st.spinner("Loading order lines from MySQL…"):
        raw = read_frame(engine, ORDER_LINES, {"start_date": "2024-01-01", "end_date": "2027-01-01"})
    df = clean_order_lines(raw)
except Exception as exc:
    st.error("Could not read the database. Check MySQL is running, the schema exists, and local .env values are correct.")
    st.code(str(exc))
    st.info("Copy .env.example to .env and enter credentials locally. The .env file is ignored by Git.")
    st.stop()

if df.empty:
    st.warning("No order lines found in the selected time window.")
    st.stop()

min_date, max_date = df["order_date"].min().date(), df["order_date"].max().date()
date_range = st.sidebar.date_input("Order date range", (min_date, max_date), min_value=min_date, max_value=max_date)
categories = sorted(df["category"].dropna().unique().tolist())
chosen_categories = st.sidebar.multiselect("Categories", categories, default=categories)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
    filtered = df[(df.order_date >= start) & (df.order_date < end) & df.category.isin(chosen_categories)]
else:
    filtered = df[df.category.isin(chosen_categories)]

m = summarize(filtered)
a, b, c, d, e = st.columns(5)
a.metric("Merchandise revenue", f"${m['revenue']:,.0f}")
b.metric("Orders", f"{m['orders']:,}")
c.metric("Customers", f"{m['customers']:,}")
d.metric("Average order value", f"${m['aov']:,.2f}")
e.metric("Repeat customers", f"{m['repeat_share']:.1%}")
st.caption(f"Showing {len(filtered):,} valid order lines from {len(raw):,} database rows after cleaning.")

if filtered.empty:
    st.warning("No data matches these filters.")
    st.stop()

delivered = filtered[filtered.order_status == "delivered"]
monthly = delivered.assign(month=delivered.order_date.dt.to_period("M").dt.to_timestamp()).groupby("month", as_index=False).agg(revenue=("line_revenue", "sum"))
products = filtered.groupby("product_name", as_index=False).agg(revenue=("line_revenue", "sum")).nlargest(10, "revenue")
customers = filtered.groupby("customer_unique_id", as_index=False).agg(revenue=("line_revenue", "sum")).nlargest(10, "revenue")
category = filtered.groupby("category", as_index=False).agg(revenue=("line_revenue", "sum")).sort_values("revenue")
region = filtered.groupby("state", as_index=False).agg(revenue=("line_revenue", "sum")).sort_values("revenue")
order_values = filtered.groupby("order_id", as_index=False).agg(order_value=("line_revenue", "sum"))
repeat = filtered.groupby("customer_unique_id").agg(orders=("order_id", "nunique"), revenue=("line_revenue", "sum")).reset_index()
repeat["customer_type"] = repeat.orders.map(lambda n: "Repeat" if n > 1 else "One-time")
repeat_mix = repeat.groupby("customer_type", as_index=False).agg(customers=("customer_unique_id", "count"), revenue=("revenue", "sum"))

row1, row2 = st.columns(2)
row1.plotly_chart(px.line(monthly, x="month", y="revenue", markers=True, title="1. Delivered revenue by month"), use_container_width=True)
row1.plotly_chart(px.bar(products.sort_values("revenue"), x="revenue", y="product_name", orientation="h", title="2. Top products by merchandise revenue"), use_container_width=True)
row1.plotly_chart(px.histogram(order_values, x="order_value", nbins=30, title="3. Order value distribution"), use_container_width=True)
row2.plotly_chart(px.bar(customers.sort_values("revenue"), x="revenue", y="customer_unique_id", orientation="h", title="4. Top customers by revenue"), use_container_width=True)
row2.plotly_chart(px.bar(category, x="revenue", y="category", orientation="h", title="5. Revenue by category"), use_container_width=True)
row2.plotly_chart(px.bar(region, x="state", y="revenue", title="6. Revenue by customer state"), use_container_width=True)
st.plotly_chart(px.bar(repeat_mix, x="customer_type", y="customers", color="customer_type", title="7. One-time vs repeat customers"), use_container_width=True)

st.subheader("Customer RFM segments")
st.write("RFM summarizes how recently each customer bought, how often they ordered, and how much they spent. K-Means groups customers with similar standardized RFM patterns; segment numbers are cluster labels, not grades.")
rfm = build_rfm(filtered)
if not rfm.empty:
    segment_summary = rfm.groupby("segment", as_index=False).agg(customers=("customer_unique_id", "count"), avg_recency_days=("recency_days", "mean"), avg_orders=("frequency_orders", "mean"), avg_revenue=("monetary_revenue", "mean"))
    st.plotly_chart(px.scatter(rfm, x="frequency_orders", y="monetary_revenue", color="segment", hover_data=["recency_days"], title="Customer segments: frequency vs spend"), use_container_width=True)
    st.dataframe(segment_summary.round(2), use_container_width=True)
