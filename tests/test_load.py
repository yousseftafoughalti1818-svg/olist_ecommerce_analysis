import pytest

from olist_analysis.load import build_database, run_sql


def test_all_tables_loaded(conn):
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"orders", "order_items", "customers", "products"} <= tables


def test_view_one_row_per_order(conn):
    v = run_sql(conn, "SELECT * FROM v_orders")
    assert len(v) == 4
    assert v["order_id"].is_unique


def test_revenue_excludes_freight(conn):
    o1 = run_sql(conn, "SELECT items_value, freight_value FROM v_orders WHERE order_id = 'o1'").iloc[0]
    assert o1["items_value"] == 150.0
    assert o1["freight_value"] == 15.0


def test_late_delivery_flag(conn):
    v = run_sql(conn, "SELECT order_id, is_late, delay_days FROM v_orders").set_index("order_id")
    assert v.loc["o1", "is_late"] == 0
    assert v.loc["o3", "is_late"] == 1
    assert v.loc["o3", "delay_days"] == 10


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        build_database(tmp_path, tmp_path / "x.db")
