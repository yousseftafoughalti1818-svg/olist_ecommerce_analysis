"""Export a star schema (facts + dimensions) as CSV files ready for Power BI."""
from __future__ import annotations

import sqlite3

import pandas as pd

from olist_analysis import config
from olist_analysis.load import run_sql

QUERIES = {
    "fact_orders": """
        SELECT v.order_id, v.customer_unique_id, date(v.purchase_ts) AS order_date,
               v.order_status, v.n_items, ROUND(v.items_value, 2) AS revenue,
               ROUND(v.freight_value, 2) AS freight, ROUND(v.delivery_days, 1) AS delivery_days,
               v.delay_days, v.is_late, v.review_score,
               (SELECT payment_type FROM order_payments p WHERE p.order_id = v.order_id
                ORDER BY payment_value DESC LIMIT 1) AS main_payment_type
        FROM v_orders v
        WHERE v.purchase_ts >= :start AND v.purchase_ts < :end""",
    "fact_order_items": """
        SELECT i.order_id, i.order_item_id, i.product_id, i.seller_id,
               date(i.purchase_ts) AS order_date, i.order_status,
               ROUND(i.price, 2) AS price, ROUND(i.freight_value, 2) AS freight
        FROM v_items i
        WHERE i.purchase_ts >= :start AND i.purchase_ts < :end""",
    "dim_customers": """
        SELECT customer_unique_id, MIN(customer_city) AS city, MIN(customer_state) AS state
        FROM customers GROUP BY customer_unique_id""",
    "dim_products": """
        SELECT p.product_id,
               COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category,
               p.product_weight_g, p.product_photos_qty
        FROM products p
        LEFT JOIN category_translation t ON t.product_category_name = p.product_category_name""",
    "dim_sellers": "SELECT seller_id, seller_city AS city, seller_state AS state FROM sellers",
}


def date_dimension() -> pd.DataFrame:
    dates = pd.date_range(config.PERIOD_START, pd.Timestamp(config.PERIOD_END) - pd.Timedelta(days=1))
    return pd.DataFrame({
        "date": dates.date,
        "year": dates.year,
        "month_num": dates.month,
        "month": dates.strftime("%Y-%m"),
        "quarter": "Q" + dates.quarter.astype(str),
        "weekday": dates.day_name(),
        "is_weekend": dates.dayofweek >= 5,
    })


def export(conn: sqlite3.Connection) -> list[str]:
    config.POWERBI_DATA_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, sql in QUERIES.items():
        run_sql(conn, sql).to_csv(config.POWERBI_DATA_DIR / f"{name}.csv", index=False)
        written.append(name)
    date_dimension().to_csv(config.POWERBI_DATA_DIR / "dim_date.csv", index=False)
    written.append("dim_date")
    return written
