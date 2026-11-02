"""Data quality checks on the raw tables.

Each check is a SQL query returning the number of problematic rows.
Results are saved to reports/data_quality.md so problems are documented
before any analysis.
"""
from __future__ import annotations

import sqlite3

import pandas as pd

from olist_analysis import config

# (check name, table, SQL counting failing rows, SQL counting total rows, severity)
CHECKS = [
    ("Duplicate order_id", "orders",
     "SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM orders", "SELECT COUNT(*) FROM orders", "high"),
    ("Order without customer", "orders",
     "SELECT COUNT(*) FROM orders o LEFT JOIN customers c ON c.customer_id = o.customer_id "
     "WHERE c.customer_id IS NULL", "SELECT COUNT(*) FROM orders", "high"),
    ("Item without order", "order_items",
     "SELECT COUNT(*) FROM order_items i LEFT JOIN orders o ON o.order_id = i.order_id "
     "WHERE o.order_id IS NULL", "SELECT COUNT(*) FROM order_items", "high"),
    ("Item without product", "order_items",
     "SELECT COUNT(*) FROM order_items i LEFT JOIN products p ON p.product_id = i.product_id "
     "WHERE p.product_id IS NULL", "SELECT COUNT(*) FROM order_items", "high"),
    ("Negative or zero price", "order_items",
     "SELECT COUNT(*) FROM order_items WHERE price <= 0", "SELECT COUNT(*) FROM order_items", "high"),
    ("Delivered order without delivery date", "orders",
     "SELECT COUNT(*) FROM orders WHERE order_status = 'delivered' "
     "AND order_delivered_customer_date IS NULL", "SELECT COUNT(*) FROM orders", "medium"),
    ("Delivered before purchase", "orders",
     "SELECT COUNT(*) FROM orders WHERE order_delivered_customer_date < order_purchase_timestamp",
     "SELECT COUNT(*) FROM orders", "medium"),
    ("Order without items", "orders",
     "SELECT COUNT(*) FROM orders o LEFT JOIN order_items i ON i.order_id = o.order_id "
     "WHERE i.order_id IS NULL", "SELECT COUNT(*) FROM orders", "medium"),
    ("Order with several reviews", "order_reviews",
     "SELECT COUNT(*) FROM (SELECT order_id FROM order_reviews GROUP BY order_id HAVING COUNT(*) > 1)",
     "SELECT COUNT(DISTINCT order_id) FROM order_reviews", "low"),
    ("Product without category", "products",
     "SELECT COUNT(*) FROM products WHERE product_category_name IS NULL",
     "SELECT COUNT(*) FROM products", "low"),
    ("Category without English translation", "products",
     "SELECT COUNT(DISTINCT p.product_category_name) FROM products p "
     "LEFT JOIN category_translation t ON t.product_category_name = p.product_category_name "
     "WHERE p.product_category_name IS NOT NULL AND t.product_category_name IS NULL",
     "SELECT COUNT(DISTINCT product_category_name) FROM products", "low"),
    ("Payment with zero value", "order_payments",
     "SELECT COUNT(*) FROM order_payments WHERE payment_value <= 0",
     "SELECT COUNT(*) FROM order_payments", "low"),
]


def run_checks(conn: sqlite3.Connection) -> pd.DataFrame:
    rows = []
    for name, table, failing_sql, total_sql, severity in CHECKS:
        failing = conn.execute(failing_sql).fetchone()[0]
        total = conn.execute(total_sql).fetchone()[0]
        rows.append({
            "check": name, "table": table, "severity": severity,
            "failing_rows": failing, "total_rows": total,
            "failing_pct": round(100 * failing / total, 3) if total else 0.0,
            "status": "OK" if failing == 0 else "WARNING",
        })
    return pd.DataFrame(rows)


def write_report(results: pd.DataFrame) -> None:
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(config.REPORTS_DIR / "data_quality.csv", index=False)
    lines = [
        "# Data quality report", "",
        "| Check | Table | Severity | Failing rows | % | Status |",
        "|---|---|---|---|---|---|",
    ]
    for r in results.itertuples():
        lines.append(f"| {r.check} | {r.table} | {r.severity} | {r.failing_rows:,} "
                     f"| {r.failing_pct} | {r.status} |")
    lines += ["", "How the analysis handles these issues:",
              "- only orders with status `delivered` are used for sales KPIs;",
              "- orders without delivery date are excluded from delivery-time metrics;",
              "- orders with several reviews use the average score;",
              "- products without category are grouped as `unknown`."]
    (config.REPORTS_DIR / "data_quality.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
