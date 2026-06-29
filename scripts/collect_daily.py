from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from islandedge.agent_reach import (
    SearchRequest,
    collect_reddit,
    collect_twitter,
    dedupe_posts,
    filter_posts_for_date,
    reddit_queries,
    twitter_queries,
)
from islandedge.config import load_settings
from islandedge.contestants import active_contestants, contestants_for_season
from islandedge.ingest import extract_mentions
from islandedge.storage import delete_mentions_for_posts, insert_mentions, insert_raw_posts, upsert_contestants


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect daily Agent-Reach social data for IslandEdge.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Feature date in YYYY-MM-DD format.")
    parser.add_argument("--day", type=int, required=True, help="Love Island season day represented by this collection.")
    parser.add_argument("--source", choices=("twitter", "reddit", "all"), default="all")
    parser.add_argument("--dry-run", action="store_true", help="Print queries without calling Agent-Reach.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = load_settings()
    feature_date = date.fromisoformat(args.date)
    contestants = active_contestants(settings.season, args.day)
    upsert_contestants(settings.database_path, settings.season, contestants_for_season(settings.season))

    requests: list[SearchRequest] = []
    if args.source in ("twitter", "all"):
        requests.extend(
            SearchRequest(settings.season, feature_date, "twitter", query)
            for query in twitter_queries(contestants)
        )
    if args.source in ("reddit", "all"):
        requests.extend(
            SearchRequest(settings.season, feature_date, "reddit", query, subreddit="LoveIslandUSA")
            for query in reddit_queries(contestants)
        )

    if args.dry_run:
        for request in requests:
            print(f"{request.source}: {request.query}")
        return

    raw_posts: list[dict] = []
    for request in requests:
        if request.source == "twitter":
            raw_posts.extend(collect_twitter(request, settings.agent_reach_timeout_seconds))
        else:
            raw_posts.extend(collect_reddit(request, settings.agent_reach_timeout_seconds))

    raw_posts = dedupe_posts(filter_posts_for_date(raw_posts, feature_date))
    mentions = extract_mentions(raw_posts, contestants)
    insert_raw_posts(settings.database_path, raw_posts)
    delete_mentions_for_posts(settings.database_path, (post["id"] for post in raw_posts))
    insert_mentions(settings.database_path, mentions)
    print(f"Collected {len(raw_posts)} posts and {len(mentions)} contestant mentions for {feature_date}.")


if __name__ == "__main__":
    main()
