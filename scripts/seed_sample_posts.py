from __future__ import annotations

from datetime import date

from islandedge.config import load_settings
from islandedge.contestants import contestants_for_season
from islandedge.ingest import extract_mentions
from islandedge.storage import delete_mentions_for_posts, insert_mentions, insert_raw_posts, upsert_contestants


def main() -> None:
    settings = load_settings()
    today = date.today().isoformat()
    contestants = contestants_for_season(settings.season)
    upsert_contestants(settings.database_path, settings.season, contestants)
    raw_posts = [
        {
            "id": f"sample-twitter-bryce-{today}",
            "season": settings.season,
            "source": "twitter",
            "source_id": f"sample-twitter-bryce-{today}",
            "source_url": None,
            "author": "sample",
            "text": "Bryce and Trinity are my Love Island USA favorites, their chemistry is winner energy.",
            "posted_at": f"{today}T12:00:00",
            "query": "sample",
            "subreddit": None,
            "engagement": 40,
        },
        {
            "id": f"sample-reddit-trinity-{today}",
            "season": settings.season,
            "source": "reddit",
            "source_id": f"sample-reddit-trinity-{today}",
            "source_url": None,
            "author": "sample",
            "text": "On r/LoveIslandUSA Trinity is the queen of the villa right now.",
            "posted_at": f"{today}T12:00:00",
            "query": "sample",
            "subreddit": "LoveIslandUSA",
            "engagement": 25,
        },
    ]
    mentions = extract_mentions(raw_posts, contestants)
    insert_raw_posts(settings.database_path, raw_posts)
    delete_mentions_for_posts(settings.database_path, (post["id"] for post in raw_posts))
    insert_mentions(settings.database_path, mentions)
    print(f"Seeded {len(raw_posts)} sample posts and {len(mentions)} mentions.")


if __name__ == "__main__":
    main()
