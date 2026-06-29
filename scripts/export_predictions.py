from __future__ import annotations

import argparse
from pathlib import Path

from islandedge.config import load_settings
from islandedge.export import export_predictions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export frontend-ready IslandEdge predictions JSON.")
    parser.add_argument("--out", default="public/data/processed/predictions/season8_daily.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = load_settings()
    payload = export_predictions(settings.database_path, settings.season, Path(args.out))
    print(f"Exported {len(payload['days'])} prediction day(s) to {args.out}.")


if __name__ == "__main__":
    main()
