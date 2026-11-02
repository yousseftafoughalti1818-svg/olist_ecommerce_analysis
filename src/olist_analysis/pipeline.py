"""Full pipeline: CSV -> SQLite -> data quality -> SQL analyses -> charts -> Power BI export.

Usage:
    python -m olist_analysis.pipeline
"""
from __future__ import annotations

import json
import logging

from olist_analysis import analysis, config, export_powerbi, quality
from olist_analysis.load import build_database, connect

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logging.getLogger("matplotlib").setLevel(logging.WARNING)
log = logging.getLogger("olist.pipeline")


def run(raw_dir=None, db_path=None) -> dict:
    db = build_database(raw_dir, db_path)
    log.info("Database ready: %s", db)
    with connect(db) as conn:
        checks = quality.run_checks(conn)
        quality.write_report(checks)
        log.info("Data quality: %d checks, %d warnings", len(checks), (checks["status"] != "OK").sum())

        results = analysis.run_queries(conn)
        analysis.make_figures(results)
        facts = analysis.write_insights(results)
        tables = export_powerbi.export(conn)
        log.info("Power BI files: %s", ", ".join(tables))

    (config.REPORTS_DIR / "key_figures.json").write_text(json.dumps(facts, indent=2), encoding="utf-8")
    log.info("Done. See reports/insights.md")
    return facts


if __name__ == "__main__":
    run()
