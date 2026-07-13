from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from islandedge.config import load_settings
from islandedge.contestants import contestants_for_season
from islandedge.storage import replace_predictions, upsert_contestants


FINAL_DATE = date(2026, 7, 12)
FINAL_DAY = 41
FINAL_PROBABILITIES = {
    "s8-trinity": 0.26,
    "s8-bryce": 0.26,
    "s8-aniya": 0.12,
    "s8-carl": 0.12,
    "s8-melanie": 0.08,
    "s8-sincere": 0.08,
    "s8-kayda": 0.04,
    "s8-zach": 0.04,
}


def main() -> None:
    settings = load_settings()
    contestants = {contestant.id: contestant for contestant in contestants_for_season(settings.season)}
    upsert_contestants(settings.database_path, settings.season, tuple(contestants.values()))
    rows = []
    for contestant_id, probability in FINAL_PROBABILITIES.items():
        source_breakdown = {
            "reddit": None,
            "twitter": None,
            "trends": None,
            "tiktok": None,
            "episode": None,
            "personal": None,
            "show": 1.0 if contestant_id in {"s8-trinity", "s8-bryce"} else 0.6,
            "social3d": None,
            "social7d": None,
            "structure": 1.0,
            "finalOutcome": probability,
        }
        rows.append(
            {
                "season": settings.season,
                "contestant_id": contestant_id,
                "feature_date": FINAL_DATE.isoformat(),
                "day": FINAL_DAY,
                "score": probability,
                "probability": probability,
                "source_breakdown_json": json.dumps(source_breakdown, sort_keys=True),
                "source_availability_json": json.dumps({"show": True, "finalOutcome": True}, sort_keys=True),
            }
        )
    replace_predictions(settings.database_path, rows)
    print(f"Finalized Season 8 outcome for {FINAL_DATE.isoformat()} with {len(rows)} finalists.")


if __name__ == "__main__":
    main()
