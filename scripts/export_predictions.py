from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from islandedge.config import load_settings
from islandedge.export import export_predictions, export_source_health


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export frontend-ready IslandEdge predictions JSON.")
    parser.add_argument("--out", default="public/data/processed/predictions/season8_daily.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = load_settings()
    payload = export_predictions(settings.database_path, settings.season, Path(args.out))
    export_source_health(settings.database_path, settings.season, Path("public/data/processed/source_health.json"))
    print(f"Exported {len(payload['days'])} prediction day(s) to {args.out}.")


if __name__ == "__main__":
    main()
