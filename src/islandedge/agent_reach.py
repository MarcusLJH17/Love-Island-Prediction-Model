from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Iterable

from islandedge.contestants import Contestant

PRIORITY_CONTESTANT_IDS = (
    "s8-trinity",
    "s8-bryce",
    "s8-aniya",
    "s8-carl",
    "s8-kenzie",
    "s8-dylan",
    "s8-jen",
    "s8-gal",
    "s8-corbin",
    "s8-parmida",
    "s8-kc",
    "s8-titi",
)


@dataclass(frozen=True)
class SearchRequest:
    season: int
    feature_date: date
    source: str
    query: str
    subreddit: str | None = None


def run_agent_reach(command: list[str], timeout_seconds: int) -> str:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    home = os.path.expanduser("~")
    extra_paths = [
        os.path.join(home, ".local", "bin"),
        os.path.join(os.getenv("APPDATA", ""), "npm"),
        os.path.join(os.getenv("APPDATA", ""), "Python", "Python312", "Scripts"),
    ]
    env["PATH"] = os.pathsep.join([*extra_paths, env.get("PATH", "")])
    if command[0] == "opencli":
        opencli_entry = os.path.join(
            os.getenv("APPDATA", ""),
            "npm",
            "node_modules",
            "@jackwener",
            "opencli",
            "dist",
            "src",
            "main.js",
        )
        resolved_command = ["node", opencli_entry, *command[1:]]
    else:
        executable = shutil.which(command[0], path=env["PATH"])
        resolved_command = [executable or command[0], *command[1:]]
    completed = subprocess.run(
        resolved_command,
        check=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        text=True,
        timeout=timeout_seconds,
    )
    return completed.stdout


def twitter_queries(contestants: Iterable[Contestant]) -> list[str]:
    queries: list[str] = []
    ordered = priority_order(contestants)
    for contestant in ordered:
        queries.append(f"{contestant.display_name} Love Island USA")
    for contestant in ordered:
        if contestant.full_name != contestant.display_name:
            queries.append(f"{contestant.full_name} Love Island USA")
    queries.extend(["Love Island USA", "LIUSA", "Casa Amor Love Island USA"])
    return dedupe(queries)


def reddit_queries(contestants: Iterable[Contestant], subreddit: str = "LoveIslandUSA") -> list[str]:
    queries = [contestant.display_name for contestant in priority_order(contestants)]
    queries.extend(["recoupling", "casa", "episode"])
    return dedupe(queries)


def priority_order(contestants: Iterable[Contestant]) -> list[Contestant]:
    priority = {contestant_id: index for index, contestant_id in enumerate(PRIORITY_CONTESTANT_IDS)}
    return sorted(
        contestants,
        key=lambda contestant: (
            priority.get(getattr(contestant, "id", ""), len(priority)),
            contestant.display_name.casefold(),
        ),
    )


def collect_twitter(request: SearchRequest, timeout_seconds: int) -> list[dict]:
    output = run_agent_reach(
        ["opencli", "twitter", "search", request.query, "--product", "live", "--limit", "25", "-f", "json"],
        timeout_seconds,
    )
    return parse_output(output, request)


def collect_reddit(request: SearchRequest, timeout_seconds: int) -> list[dict]:
    command = ["opencli", "reddit", "search", request.query, "--sort", "new", "--time", "day", "--limit", "25", "-f", "json"]
    if request.subreddit:
        command.extend(["--subreddit", request.subreddit])
    output = run_agent_reach(command, timeout_seconds)
    return parse_output(output, request)


def parse_output(output: str, request: SearchRequest) -> list[dict]:
    rows: list[dict] = []
    for index, payload in enumerate(iter_payloads(output)):
        text = payload_text(payload)
        if not text.strip():
            continue
        source_id = str(payload.get("id") or payload.get("url") or stable_id(request.source, request.query, text, index))
        posted_at = parse_timestamp(
            payload.get("created_utc") or payload.get("timestamp") or payload.get("created_at") or payload.get("date"),
            request.feature_date,
        )
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
    try:
        payload = json.loads(output)
    except json.JSONDecodeError:
        payload = None
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                yield item
        return
    if isinstance(payload, dict):
        yield payload
        return

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


def payload_text(payload: dict) -> str:
    title = str(payload.get("title") or "").strip()
    body = str(payload.get("selftext") or payload.get("body") or payload.get("text") or "").strip()
    return "\n\n".join(part for part in (title, body) if part)


def parse_timestamp(value: object, fallback_date: date) -> str:
    if value is None:
        return f"{fallback_date.isoformat()}T12:00:00"
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, timezone.utc).isoformat()
    text = str(value)
    if text.isdigit():
        return datetime.fromtimestamp(int(text), timezone.utc).isoformat()
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).isoformat()
    except ValueError:
        return f"{fallback_date.isoformat()}T12:00:00"


def stable_id(*parts: object) -> str:
    payload = "|".join(str(part) for part in parts)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def posted_date(row: dict) -> date:
    return datetime.fromisoformat(str(row["posted_at"]).replace("Z", "+00:00")).date()


def filter_posts_for_date(rows: Iterable[dict], feature_date: date) -> list[dict]:
    return [row for row in rows if posted_date(row) == feature_date]


def dedupe_posts(rows: Iterable[dict]) -> list[dict]:
    seen: set[str] = set()
    result: list[dict] = []
    for row in rows:
        key = str(row["id"])
        if key in seen:
            continue
        seen.add(key)
        result.append(row)
    return result


def contestant_query_names(contestant: Contestant) -> list[str]:
    names = [contestant.display_name, contestant.full_name]
    names.extend(alias for alias in contestant.aliases if len(alias) > 2)
    seen: set[str] = set()
    result: list[str] = []
    for name in names:
        key = name.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(name)
    return result


def dedupe(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
