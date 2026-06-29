from __future__ import annotations

from datetime import datetime

from islandedge.context import match_mentions
from islandedge.contestants import Contestant


def extract_mentions(raw_posts: list[dict], contestants: tuple[Contestant, ...]) -> list[dict]:
    rows: list[dict] = []
    for post in raw_posts:
        posted_date = datetime.fromisoformat(str(post["posted_at"]).replace("Z", "+00:00")).date().isoformat()
        matches = match_mentions(str(post["text"]), contestants)
        for match in matches:
            rows.append(
                {
                    "raw_post_id": post["id"],
                    "season": post["season"],
                    "contestant_id": match.contestant_id,
                    "alias": match.alias,
                    "confidence": match.confidence,
                    "sentiment": match.sentiment,
                    "context_terms": ",".join(match.context_terms),
                    "posted_date": posted_date,
                    "source": post["source"],
                    "engagement": post["engagement"],
                }
            )
    return rows
