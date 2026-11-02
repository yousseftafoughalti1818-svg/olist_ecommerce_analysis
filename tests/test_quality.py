from olist_analysis.quality import CHECKS, run_checks


def test_every_check_runs(conn):
    res = run_checks(conn)
    assert len(res) == len(CHECKS)
    assert set(res["status"]) <= {"OK", "WARNING"}


def test_detects_product_without_category(conn):
    res = run_checks(conn).set_index("check")
    assert res.loc["Product without category", "failing_rows"] == 1
    assert res.loc["Duplicate order_id", "status"] == "OK"
