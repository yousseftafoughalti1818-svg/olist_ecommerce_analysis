"""Run the SQL analyses, save result tables, charts and a summary of the findings."""
from __future__ import annotations

import sqlite3

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from olist_analysis import config
from olist_analysis.load import run_sql

BLUE, GREY, RED = "#2F6DB5", "#B8C2CC", "#C8553D"


def run_queries(conn: sqlite3.Connection) -> dict[str, pd.DataFrame]:
    """Execute every file in sql/analysis and save the result as CSV."""
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    results = {}
    for path in sorted((config.SQL_DIR / "analysis").glob("*.sql")):
        name = path.stem.split("_", 1)[1]  # "02_monthly_sales" -> "monthly_sales"
        df = run_sql(conn, path.read_text(encoding="utf-8"))
        df.to_csv(config.TABLES_DIR / f"{name}.csv", index=False)
        results[name] = df
    return results


def _style(ax, title, xlabel="", ylabel=""):
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold")
    ax.set(xlabel=xlabel, ylabel=ylabel)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3)


def _save(fig, name):
    fig.tight_layout()
    fig.savefig(config.FIGURES_DIR / name, dpi=130)
    plt.close(fig)


def make_figures(r: dict[str, pd.DataFrame]) -> None:
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    m = r["monthly_sales"]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(m["month"], m["revenue"] / 1000, color=BLUE, marker="o", lw=2)
    peak = m.loc[m["revenue"].idxmax()]
    ax.annotate(f"Peak: {peak['month']}", (peak["month"], peak["revenue"] / 1000),
                textcoords="offset points", xytext=(-30, 10), color=RED)
    ax.tick_params(axis="x", rotation=45)
    _style(ax, "Monthly revenue (delivered orders)", ylabel="Revenue (k BRL)")
    _save(fig, "monthly_revenue.png")

    c = r["categories"].head(15).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(c["category"], c["revenue"] / 1000, color=BLUE)
    _style(ax, "Top 15 categories by revenue", xlabel="Revenue (k BRL)")
    ax.grid(axis="x", alpha=0.3)
    ax.grid(axis="y", visible=False)
    _save(fig, "top_categories.png")

    d = r["delivery_vs_reviews"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = [BLUE] + [RED] * (len(d) - 1)
    bars = ax.bar(d["delay_bucket"].str[3:], d["avg_review_score"], color=colors)
    ax.bar_label(bars, fmt="%.2f", padding=3)
    ax.set_ylim(0, 5.3)
    _style(ax, "Average review score by delivery delay", ylabel="Review score (1-5)")
    _save(fig, "delay_vs_review.png")

    s = r["states"].sort_values("avg_delivery_days")
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(s["state"], s["avg_delivery_days"], color=GREY)
    for state in ("SP", "RJ", "MG"):
        idx = list(s["state"]).index(state) if state in set(s["state"]) else None
        if idx is not None:
            ax.patches[idx].set_color(BLUE)
    _style(ax, "Average delivery time by state (blue = 3 largest markets)", ylabel="Days")
    _save(fig, "delivery_days_by_state.png")

    sel = r["sellers"]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(sel["decile"].astype(str), sel["revenue_share_pct"], color=[BLUE] + [GREY] * (len(sel) - 1))
    _style(ax, "Revenue share by seller decile (1 = top 10% sellers)",
           xlabel="Seller decile", ylabel="% of revenue")
    _save(fig, "seller_concentration.png")


def write_insights(r: dict[str, pd.DataFrame]) -> dict:
    k = r["kpis"].iloc[0]
    m = r["monthly_sales"]
    cats = r["categories"]
    d = r["delivery_vs_reviews"].set_index("delay_bucket")
    rep = r["repeat_customers"].set_index("segment")
    sel = r["sellers"]
    states = r["states"]
    pay = r["payments"].set_index("payment_type")

    first_q = m[m["month"].between("2017-01", "2017-03")]["revenue"].mean()
    last_q = m[m["month"].between("2018-06", "2018-08")]["revenue"].mean()
    on_time = d.iloc[0]
    very_late = d.iloc[-1]
    top3 = states.head(3)
    n_top_cats = int((cats["cumulative_share_pct"] < 50).sum()) + 1

    facts = {
        "orders": int(k["orders"]),
        "customers": int(k["customers"]),
        "revenue": float(k["revenue"]),
        "avg_order_value": float(k["avg_order_value"]),
        "late_pct": float(k["late_pct"]),
        "avg_review": float(k["avg_review_score"]),
        "growth_pct": round(100 * (last_q / first_q - 1), 0),
        "peak_month": m.loc[m["revenue"].idxmax(), "month"],
        "n_categories": len(cats),
        "n_top_cats_50pct": n_top_cats,
        "review_on_time": float(on_time["avg_review_score"]),
        "review_very_late": float(very_late["avg_review_score"]),
        "low_review_on_time": float(on_time["low_review_pct"]),
        "low_review_very_late": float(very_late["low_review_pct"]),
        "one_time_customers_pct": float(rep.loc["1 order", "customers_pct"]),
        "top10_sellers_share": float(sel.iloc[0]["revenue_share_pct"]),
        "top3_states": ", ".join(top3["state"]),
        "top3_states_share": round(100 * top3["revenue"].sum() / states["revenue"].sum(), 1),
        "credit_card_pct": float(pay.loc["credit_card", "orders_pct"]) if "credit_card" in pay.index else None,
    }

    lines = [
        "# Key findings", "",
        f"Period: {config.PERIOD_START[:7]} to 2018-08, delivered orders only.", "",
        f"- **{facts['orders']:,} orders**, {facts['customers']:,} customers, "
        f"**{facts['revenue']:,.0f} BRL** revenue, average basket {facts['avg_order_value']:.2f} BRL.",
        f"- Growth: monthly revenue is **{facts['growth_pct']:+.0f}%** higher in summer 2018 than in "
        f"Q1 2017; best month: {facts['peak_month']} (Black Friday).",
        f"- Catalogue: {facts['n_top_cats_50pct']} categories out of {facts['n_categories']} make half "
        "of the revenue.",
        f"- Delivery: {facts['late_pct']}% of orders arrive after the estimated date. Average review "
        f"falls from **{facts['review_on_time']}** (on time) to **{facts['review_very_late']}** "
        f"(15+ days late); 1-2 star reviews go from {facts['low_review_on_time']}% to "
        f"{facts['low_review_very_late']}%.",
        f"- Loyalty: **{facts['one_time_customers_pct']}%** of customers ordered only once.",
        f"- Sellers: the top 10% of sellers make **{facts['top10_sellers_share']}%** of revenue.",
        f"- Geography: {facts['top3_states']} make {facts['top3_states_share']}% of revenue.",
    ]
    if facts["credit_card_pct"] is not None:
        lines.append(f"- Payment: {facts['credit_card_pct']}% of orders are paid by credit card.")
    (config.REPORTS_DIR / "insights.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return facts
