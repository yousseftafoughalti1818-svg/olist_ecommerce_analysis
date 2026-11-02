"""Project paths and settings."""
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

RAW_DIR = ROOT_DIR / "data" / "raw"
DB_PATH = ROOT_DIR / "data" / "olist.db"
SQL_DIR = ROOT_DIR / "sql"
REPORTS_DIR = ROOT_DIR / "reports"
TABLES_DIR = REPORTS_DIR / "tables"
FIGURES_DIR = REPORTS_DIR / "figures"
POWERBI_DATA_DIR = ROOT_DIR / "powerbi" / "data"

DATA_URL = "https://raw.githubusercontent.com/olist/work-at-olist-data/master/datasets/"

# table name in the database -> CSV file from Olist
TABLES = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

# Analysis period: complete months only (2016 is almost empty, data stops in early Sept 2018)
PERIOD_START = "2017-01-01"
PERIOD_END = "2018-09-01"  # excluded
