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
