from olist_analysis import analysis, export_powerbi


def test_kpis_only_delivered_orders(conn, tmp_outputs):
    r = analysis.run_queries(conn)
    k = r["kpis"].iloc[0]
    assert k["orders"] == 3  # the canceled order is excluded
    assert k["customers"] == 2
    assert k["revenue"] == 450


def test_repeat_customers(conn, tmp_outputs):
    rep = analysis.run_queries(conn)["repeat_customers"].set_index("segment")
    assert rep.loc["1 order", "customers"] == 1
    assert rep.loc["2 orders", "customers"] == 1


def test_unknown_category_label(conn, tmp_outputs):
    cats = analysis.run_queries(conn)["categories"]
    assert "unknown" in set(cats["category"])
    assert abs(cats["revenue_share_pct"].sum() - 100) < 0.1


def test_full_outputs(conn, tmp_outputs):
    r = analysis.run_queries(conn)
    analysis.make_figures(r)
    facts = analysis.write_insights(r)
    assert facts["orders"] == 3
    assert (tmp_outputs / "reports" / "figures" / "monthly_revenue.png").exists()
    assert (tmp_outputs / "reports" / "insights.md").exists()


def test_powerbi_export(conn, tmp_outputs):
    written = export_powerbi.export(conn)
    assert "fact_orders" in written and "dim_date" in written
    assert (tmp_outputs / "powerbi" / "fact_order_items.csv").exists()
