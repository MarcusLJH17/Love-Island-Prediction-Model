import json
import subprocess
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class SearchRequest:
    contestant_name: str
    season: int
    feature_date: date
    query: str


def run_agent_reach(command: list[str], timeout_seconds: int) -> str:
    completed = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    return completed.stdout


def twitter_search(request: SearchRequest, timeout_seconds: int) -> list[dict]:
    output = run_agent_reach(["twitter", "search", request.query], timeout_seconds)
    return parse_json_lines(output, source="twitter", request=request)


def reddit_search(request: SearchRequest, timeout_seconds: int) -> list[dict]:
    output = run_agent_reach(["rdt", "search", request.query], timeout_seconds)
    return parse_json_lines(output, source="reddit", request=request)


def parse_json_lines(output: str, source: str, request: SearchRequest) -> list[dict]:
    rows = []
    for line in output.splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        rows.append(
            {
                "season": request.season,
                "contestant_name": request.contestant_name,
                "feature_date": request.feature_date.isoformat(),
                "source": source,
                "mention_volume": 1,
                "sentiment_mean": 0,
                "sentiment_delta": 0,
                "trend_score": float(payload.get("likes", 0) or 0),
            }
        )
    return rows
