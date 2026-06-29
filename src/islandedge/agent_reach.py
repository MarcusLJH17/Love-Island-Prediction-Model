from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable

from islandedge.contestants import Contestant


@dataclass(frozen=True)
class SearchRequest:
    season: int
    feature_date: date
    source: str
    query: str
    subreddit: str | None = None


def run_agent_reach(command: list[str], timeout_seconds: int) -> str:
    completed = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    return completed.stdout


def twitter_queries(contestants: Iterable[Contestant]) -> list[str]:
    queries: list[str] = []
    for contestant in contestants:
        primary = contestant.display_name
        queries.extend(
            [
                f'"{primary}" "Love Island"',
                f'"{primary}" "Love Island USA"',
                f'"{primary}" villa',
            ]
        )
    queries.extend(['"Love Island USA"', '"LIUSA"', '"Casa Amor" "Love Island USA"'])
    return dedupe(queries)


def reddit_queries(contestants: Iterable[Contestant], subreddit: str = "LoveIslandUSA") -> list[str]:
    queries = [f"subreddit:{subreddit} {contestant.display_name}" for contestant in contestants]
    queries.extend([f"subreddit:{subreddit} recoupling", f"subreddit:{subreddit} casa", f"subreddit:{subreddit} episode"])
    return dedupe(queries)


def collect_twitter(request: SearchRequest, timeout_seconds: int) -> list[dict]:
    output = run_agent_reach(["twitter", "search", request.query], timeout_seconds)
    return parse_output(output, request)


def collect_reddit(request: SearchRequest, timeout_seconds: int) -> list[dict]:
    output = run_agent_reach(["rdt", "search", request.query], timeout_seconds)
    return parse_output(output, request)


def parse_output(output: str, request: SearchRequest) -> list[dict]:
    rows: list[dict] = []
    for index, payload in enumerate(iter_payloads(output)):
        text = str(payload.get("text") or payload.get("body") or payload.get("title") or "")
        if not text.strip():
            continue
        source_id = str(payload.get("id") or payload.get("url") or stable_id(request.source, request.query, text, index))
        posted_at = parse_timestamp(payload.get("timestamp") or payload.get("created_at") or payload.get("date"), request.feature_date)
        rows.append(
            {
                "id": stable_id(request.source, source_id),
                "season": request.season,
                "source": request.source,
                "source_id": source_id,
                "source_url": payload.get("url") or payload.get("permalink"),
                "author": payload.get("author") or payload.get("user"),
                "text": text,
                "posted_at": posted_at,
                "query": request.query,
                "subreddit": request.subreddit,
                "engagement": float(payload.get("likes") or payload.get("score") or payload.get("upvotes") or 0),
            }
        )
    return rows


def iter_payloads(output: str) -> Iterable[dict]:
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict):
                    yield item
        elif isinstance(payload, dict):
            yield payload


def parse_timestamp(value: object, fallback_date: date) -> str:
    if value is None:
        return f"{fallback_date.isoformat()}T12:00:00"
    text = str(value)
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).isoformat()
    except ValueError:
        return f"{fallback_date.isoformat()}T12:00:00"


def stable_id(*parts: object) -> str:
    payload = "|".join(str(part) for part in parts)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def dedupe(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
