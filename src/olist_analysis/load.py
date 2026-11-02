"""Load the raw CSV files into a SQLite database and create the analysis views."""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

import pandas as pd

from olist_analysis import config

log = logging.getLogger("olist.load")

INDEXES = [
    "CREATE INDEX IF NOT EXISTS ix_orders_id ON orders(order_id)",
    "CREATE INDEX IF NOT EXISTS ix_orders_customer ON orders(customer_id)",
    "CREATE INDEX IF NOT EXISTS ix_items_order ON order_items(order_id)",
    "CREATE INDEX IF NOT EXISTS ix_items_product ON order_items(product_id)",
    "CREATE INDEX IF NOT EXISTS ix_items_seller ON order_items(seller_id)",
    "CREATE INDEX IF NOT EXISTS ix_payments_order ON order_payments(order_id)",
    "CREATE INDEX IF NOT EXISTS ix_reviews_order ON order_reviews(order_id)",
    "CREATE INDEX IF NOT EXISTS ix_customers_id ON customers(customer_id)",
    "CREATE INDEX IF NOT EXISTS ix_products_id ON products(product_id)",
]


def read_csv(path: Path) -> pd.DataFrame:
    # utf-8-sig removes the BOM present in the translation file
    df = pd.read_csv(path, encoding="utf-8-sig", dtype={
        "customer_zip_code_prefix": str, "seller_zip_code_prefix": str})
    df.columns = [c.strip() for c in df.columns]
    return df


def build_database(raw_dir: Path | None = None, db_path: Path | None = None) -> Path:
    """Create (or replace) the SQLite database from the CSV files."""
    raw_dir = Path(raw_dir) if raw_dir is not None else config.RAW_DIR
    db_path = Path(db_path) if db_path is not None else config.DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        for table, filename in config.TABLES.items():
            path = raw_dir / filename
            if not path.exists():
                raise FileNotFoundError(f"{path} not found. Run `python scripts/download_data.py`.")
            df = read_csv(path)
            df.to_sql(table, conn, if_exists="replace", index=False)
            log.info("%-22s %8d rows", table, len(df))
        for stmt in INDEXES:
            conn.execute(stmt)
        conn.executescript((config.SQL_DIR / "00_views.sql").read_text(encoding="utf-8"))
    return db_path


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    db_path = Path(db_path) if db_path is not None else config.DB_PATH
    if not db_path.exists():
        raise FileNotFoundError(f"{db_path} not found. Run the pipeline first.")
    return sqlite3.connect(db_path)


def run_sql(conn: sqlite3.Connection, sql: str) -> pd.DataFrame:
    """Run a query with the analysis period as named parameters."""
    params = {"start": config.PERIOD_START, "end": config.PERIOD_END}
    return pd.read_sql_query(sql, conn, params=params)
