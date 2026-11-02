"""Tiny synthetic Olist dataset with the same schema as the real one."""
import sqlite3

import pandas as pd
import pytest

from olist_analysis import config
from olist_analysis.load import build_database


@pytest.fixture()
def raw_dir(tmp_path):
    d = tmp_path / "raw"
    d.mkdir()
    customers = pd.DataFrame({
        "customer_id": ["c1", "c2", "c3"],
        "customer_unique_id": ["u1", "u1", "u2"],  # u1 ordered twice
        "customer_zip_code_prefix": ["01000", "01000", "20000"],
        "customer_city": ["sao paulo", "sao paulo", "rio de janeiro"],
        "customer_state": ["SP", "SP", "RJ"],
    })
    orders = pd.DataFrame({
        "order_id": ["o1", "o2", "o3", "o4"],
        "customer_id": ["c1", "c2", "c3", "c3"],
        "order_status": ["delivered", "delivered", "delivered", "canceled"],
        "order_purchase_timestamp": ["2017-03-01 10:00:00", "2017-04-01 10:00:00",
                                     "2017-04-05 10:00:00", "2017-04-06 10:00:00"],
        "order_approved_at": ["2017-03-01 11:00:00"] * 4,
        "order_delivered_carrier_date": ["2017-03-02 10:00:00"] * 4,
        "order_delivered_customer_date": ["2017-03-05 10:00:00", "2017-04-08 10:00:00",
                                          "2017-04-30 10:00:00", None],
        "order_estimated_delivery_date": ["2017-03-10 00:00:00", "2017-04-15 00:00:00",
                                          "2017-04-20 00:00:00", "2017-04-25 00:00:00"],
    })
    items = pd.DataFrame({
        "order_id": ["o1", "o1", "o2", "o3", "o4"],
        "order_item_id": [1, 2, 1, 1, 1],
        "product_id": ["p1", "p2", "p1", "p3", "p1"],
        "seller_id": ["s1", "s1", "s2", "s2", "s1"],
        "shipping_limit_date": ["2017-03-02 00:00:00"] * 5,
        "price": [100.0, 50.0, 100.0, 200.0, 80.0],
        "freight_value": [10.0, 5.0, 10.0, 30.0, 8.0],
    })
    payments = pd.DataFrame({
        "order_id": ["o1", "o2", "o3", "o4"], "payment_sequential": [1, 1, 1, 1],
        "payment_type": ["credit_card", "boleto", "credit_card", "voucher"],
        "payment_installments": [3, 1, 2, 1], "payment_value": [165.0, 110.0, 230.0, 88.0],
    })
    reviews = pd.DataFrame({
        "review_id": ["r1", "r2", "r3"], "order_id": ["o1", "o2", "o3"],
        "review_score": [5, 4, 1], "review_comment_title": [None] * 3,
        "review_comment_message": [None] * 3,
        "review_creation_date": ["2017-03-06 00:00:00"] * 3,
        "review_answer_timestamp": ["2017-03-07 00:00:00"] * 3,
    })
    products = pd.DataFrame({
        "product_id": ["p1", "p2", "p3"],
        "product_category_name": ["beleza_saude", None, "esporte_lazer"],
        "product_name_lenght": [40, 30, 20], "product_description_lenght": [200, 100, 50],
        "product_photos_qty": [1, 2, 1], "product_weight_g": [500, 300, 1200],
        "product_length_cm": [10, 10, 30], "product_height_cm": [5, 5, 20],
        "product_width_cm": [10, 10, 20],
    })
    sellers = pd.DataFrame({"seller_id": ["s1", "s2"], "seller_zip_code_prefix": ["01000", "30000"],
                            "seller_city": ["sao paulo", "belo horizonte"], "seller_state": ["SP", "MG"]})
    translation = pd.DataFrame({"product_category_name": ["beleza_saude", "esporte_lazer"],
                                "product_category_name_english": ["health_beauty", "sports_leisure"]})

    frames = {"customers": customers, "orders": orders, "order_items": items,
              "order_payments": payments, "order_reviews": reviews, "products": products,
              "sellers": sellers, "category_translation": translation}
    for table, df in frames.items():
        df.to_csv(d / config.TABLES[table], index=False)
    return d


@pytest.fixture()
def conn(raw_dir, tmp_path):
    db = build_database(raw_dir, tmp_path / "test.db")
    with sqlite3.connect(db) as c:
        yield c


@pytest.fixture()
def tmp_outputs(tmp_path, monkeypatch):
    """Redirect every output folder to a temporary directory."""
    monkeypatch.setattr(config, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(config, "TABLES_DIR", tmp_path / "reports" / "tables")
    monkeypatch.setattr(config, "FIGURES_DIR", tmp_path / "reports" / "figures")
    monkeypatch.setattr(config, "POWERBI_DATA_DIR", tmp_path / "powerbi")
    return tmp_path
