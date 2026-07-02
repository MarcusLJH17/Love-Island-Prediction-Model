from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from islandedge.config import load_settings
from islandedge.contestants import active_contestants, contestants_for_season
from islandedge.storage import replace_daily_source_metrics, upsert_contestants
from islandedge.trends import collect_trend_interest, trend_metric_rows, trend_query


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect daily Google Trends metrics for IslandEdge.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Feature date in YYYY-MM-DD format.")
    parser.add_argument("--day", type=int, required=True, help="Love Island season day represented by this collection.")
    parser.add_argument("--dry-run", action="store_true", help="Print trend queries without calling Google Trends.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = load_settings()
    feature_date = date.fromisoformat(args.date)
    contestants = active_contestants(settings.season, args.day)
    upsert_contestants(settings.database_path, settings.season, contestants_for_season(settings.season))

    if args.dry_run:
        for contestant in contestants:
            print(f"trends: {trend_query(contestant)}")
        return

    interest = collect_trend_interest(contestants, feature_date)
    rows = trend_metric_rows(settings.season, feature_date, interest)
    replace_daily_source_metrics(settings.database_path, rows)
    print(f"Collected Google Trends metrics for {len(rows)} contestants on {feature_date}.")


if __name__ == "__main__":
    main()
