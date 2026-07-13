from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from islandedge.contestants import contestants_for_season
from islandedge.storage import fetch_all


def export_predictions(database_path: Path, season: int, output_path: Path) -> dict:
    contestants = {contestant.id: contestant for contestant in contestants_for_season(season)}
    rows = fetch_all(
        database_path,
        """
        SELECT contestant_id, feature_date, day, score, probability,
               source_breakdown_json, source_availability_json
        FROM predictions
        WHERE season = ?
        ORDER BY feature_date, probability DESC
        """,
        (season,),
    )
    grouped: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for row in rows:
        contestant = contestants.get(row["contestant_id"])
        if contestant is None:
            continue
        if row["day"] < contestant.entered_day:
            continue
        if contestant.exit_day is not None and row["day"] > contestant.exit_day:
            continue
        grouped[(row["feature_date"], row["day"])].append(
            {
                "id": row["contestant_id"],
                "displayName": contestant.display_name,
                "probability": row["probability"],
                "score": row["score"],
                "sourceBreakdown": json.loads(row["source_breakdown_json"]),
                "sourceAvailable": json.loads(row["source_availability_json"]),
            }
        )
    for contestants_for_day in grouped.values():
        total = sum(contestant["probability"] for contestant in contestants_for_day)
        if total > 0:
            for contestant in contestants_for_day:
                contestant["probability"] = contestant["probability"] / total
    payload = {
        "season": season,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "days": [
            {"date": feature_date, "day": day, "contestants": contestants}
            for (feature_date, day), contestants in sorted(grouped.items())
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def export_source_health(database_path: Path, season: int, output_path: Path) -> dict:
    rows = fetch_all(
        database_path,
        """
        SELECT source, MAX(posted_at) AS latest_posted_at, MAX(collected_at) AS latest_collected_at, COUNT(*) AS raw_posts
        FROM raw_social_posts
        WHERE season = ?
        GROUP BY source
        ORDER BY source
        """,
        (season,),
    )
    metric_rows = fetch_all(
        database_path,
        """
        SELECT source, MAX(feature_date) AS latest_feature_date, SUM(mention_volume) AS mentions
        FROM daily_source_metrics
        WHERE season = ?
        GROUP BY source
        ORDER BY source
        """,
        (season,),
    )
    raw_by_source = {row["source"]: row for row in rows}
    metrics = {row["source"]: row for row in metric_rows}
    sources = []
    for source in sorted(set(raw_by_source) | set(metrics)):
        row = raw_by_source.get(source)
        metric = metrics.get(source)
        sources.append(
            {
                "source": source,
                "latestPostedAt": row["latest_posted_at"] if row else None,
                "latestCollectedAt": row["latest_collected_at"] if row else None,
                "latestFeatureDate": metric["latest_feature_date"] if metric else None,
                "rawPosts": row["raw_posts"] if row else 0,
                "mentions": metric["mentions"] if metric else 0,
            }
        )
    payload = {
        "season": season,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload
