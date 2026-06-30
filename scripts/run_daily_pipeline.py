from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run IslandEdge daily scrape/build/export pipeline.")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--day", type=int, required=True)
    parser.add_argument("--twitter-max-queries", type=int, default=8)
    parser.add_argument("--skip-scrape", action="store_true")
    return parser.parse_args()


def run(command: list[str]) -> None:
    print(" ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    args = parse_args()
    if not args.skip_scrape:
        run([sys.executable, "scripts/collect_daily.py", "--day", str(args.day), "--date", args.date, "--source", "reddit"])
        run(
            [
                sys.executable,
                "scripts/collect_daily.py",
                "--day",
                str(args.day),
                "--date",
                args.date,
                "--source",
                "twitter",
                "--max-queries",
                str(args.twitter_max_queries),
            ]
        )
    run([sys.executable, "scripts/build_features.py", "--day", str(args.day), "--date", args.date])
    run([sys.executable, "scripts/export_predictions.py"])


if __name__ == "__main__":
    main()
