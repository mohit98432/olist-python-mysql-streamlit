# Olist Marketplace Analytics — Python + MySQL + Streamlit

End-to-end portfolio project for marketplace analytics using the paired `olist_resume_analytics` MySQL schema. The dashboard extracts order lines with SQLAlchemy, cleans and analyzes them with pandas, segments customers with RFM + K-Means, and displays interactive charts in Streamlit.

## Business problem
Track revenue trends, product/category mix, customer concentration, repeat purchasing, and customer value from a normalized e-commerce model.

## Stack
MySQL 8.0, SQLAlchemy, mysql-connector-python, pandas, Plotly, scikit-learn, Streamlit, pytest.

## Setup
1. Run the companion SQL project schema and seed scripts in MySQL Workbench.
2. Create a virtual environment and install `requirements.txt`.
3. Copy `.env.example` to `.env` and enter MySQL settings locally. `.env` is ignored and must never be committed.
4. Run `streamlit run src/app.py`.
5. Run tests with `python -m pytest`.

The companion dataset is deterministic synthetic sample data; dashboard results are generated live from MySQL. No credentials, raw extracts, or fabricated output screenshots are included. See project modules for query, cleaning, analysis, and dashboard details.
