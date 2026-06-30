from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from islandedge.config import load_settings
from islandedge.storage import insert_manual_episode_entry, insert_manual_tiktok_entry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Save a manual IslandEdge entry from JSON stdin.")
    parser.add_argument("--type", choices=("tiktok", "episode"), required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = json.loads(sys.stdin.read())
    settings = load_settings()
    if args.type == "tiktok":
        insert_manual_tiktok_entry(
            settings.database_path,
            {
                "feature_date": payload["date"],
                "contestant_id": payload["contestantId"],
                "positive_sentiment": 1 if payload["positiveSentiment"] else 0,
                "visible_edit_volume": int(payload["visibleEditVolume"]),
                "comment_tone": int(payload["commentTone"]),
                "viral_momentum": int(payload["viralMomentum"]),
                "notes": payload.get("notes", ""),
            },
        )
    else:
        insert_manual_episode_entry(
            settings.database_path,
            {
                "feature_date": payload["date"],
                "contestant_id": payload["contestantId"],
                "episode_enjoyment": int(payload["episodeEnjoyment"]),
                "got_good_edit": 1 if payload["gotGoodEdit"] else 0,
                "relationship_strength": int(payload["relationshipStrength"]),
                "risk_of_dumping": int(payload["riskOfDumping"]),
                "notes": payload.get("notes", ""),
            },
        )
    print(json.dumps({"ok": True}))


if __name__ == "__main__":
    main()
