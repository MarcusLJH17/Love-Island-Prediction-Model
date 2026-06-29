from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from islandedge.config import load_settings
from islandedge.features import build_features_and_predictions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build IslandEdge daily features and prediction rows.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Feature date in YYYY-MM-DD format.")
    parser.add_argument("--day", type=int, required=True, help="Love Island season day represented by this feature set.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = load_settings()
    result = build_features_and_predictions(
        settings.database_path,
        settings.season,
        date.fromisoformat(args.date),
        args.day,
    )
    print(
        "Built "
        f"{result.metric_rows} source metrics, "
        f"{result.feature_rows} feature rows, "
        f"{result.prediction_rows} predictions."
    )


if __name__ == "__main__":
    main()
