from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEASON_START_DATES = {8: date(2026, 6, 2)}
SEASON_FINAL_DATES = {8: date(2026, 7, 12)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run IslandEdge daily scrape/build/export pipeline.")
    parser.add_argument("--date", help="Feature date in YYYY-MM-DD format. Defaults to today.")
    parser.add_argument("--day", type=int, help="Love Island season day. Defaults from the feature date.")
    parser.add_argument("--season", type=int, default=8)
    parser.add_argument(
        "--target-date",
        choices=("today", "yesterday"),
        default="today",
        help="Use yesterday for a midnight end-of-day scheduled scrape.",
    )
    parser.add_argument("--reddit-max-queries", type=int, default=16)
    parser.add_argument("--twitter-max-queries", type=int, default=8)
    parser.add_argument("--skip-scrape", action="store_true")
    parser.add_argument("--skip-trends", action="store_true")
    parser.add_argument("--force-after-finale", action="store_true", help="Run even when the feature date is after the configured finale.")
    return parser.parse_args()


def resolve_feature_date(args: argparse.Namespace) -> date:
    if args.date:
        return date.fromisoformat(args.date)
    if args.target_date == "yesterday":
        return date.today() - timedelta(days=1)
    return date.today()


def resolve_day(args: argparse.Namespace, feature_date: date) -> int:
    if args.day:
        return args.day
    start_date = SEASON_START_DATES.get(args.season)
    if start_date is None:
        raise ValueError(f"No season start date configured for season {args.season}. Pass --day explicitly.")
    return max(1, (feature_date - start_date).days + 1)


def run(command: list[str]) -> None:
    print(" ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    args = parse_args()
    feature_date = resolve_feature_date(args)
    final_date = SEASON_FINAL_DATES.get(args.season)
    if final_date is not None and feature_date > final_date and not args.force_after_finale:
        print(
            f"Season {args.season} finale date is {final_date.isoformat()}; "
            f"skipping daily update for {feature_date.isoformat()}.",
            flush=True,
        )
        return
    day = resolve_day(args, feature_date)
    date_arg = feature_date.isoformat()
    print(f"Running Season {args.season} Day {day} for {date_arg}", flush=True)
    if not args.skip_scrape:
        run(
            [
                sys.executable,
                "scripts/collect_daily.py",
                "--day",
                str(day),
                "--date",
                date_arg,
                "--source",
                "reddit",
                "--max-queries",
                str(args.reddit_max_queries),
            ]
        )
        run(
            [
                sys.executable,
                "scripts/collect_daily.py",
                "--day",
                str(day),
                "--date",
                date_arg,
                "--source",
                "twitter",
                "--max-queries",
                str(args.twitter_max_queries),
            ]
        )
        if not args.skip_trends:
            run([sys.executable, "scripts/collect_trends.py", "--day", str(day), "--date", date_arg])
    run([sys.executable, "scripts/build_features.py", "--day", str(day), "--date", date_arg])
    run([sys.executable, "scripts/export_predictions.py"])


if __name__ == "__main__":
    main()
