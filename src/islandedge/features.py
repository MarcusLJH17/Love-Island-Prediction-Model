from __future__ import annotations

import json
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path

from islandedge.contestants import Contestant, active_contestants, contestants_for_season
from islandedge.storage import (
    fetch_all,
    replace_daily_source_metrics,
    replace_model_features,
    replace_predictions,
)


SOCIAL_SOURCES = ("reddit", "twitter")
ALL_SOURCES = ("reddit", "twitter", "trends", "tiktok", "episode", "personal", "show")


@dataclass(frozen=True)
class FeatureBuildResult:
    metric_rows: int
    feature_rows: int
    prediction_rows: int


def build_daily_source_metrics(database_path, season: int) -> int:
    mention_rows = fetch_all(
        database_path,
        """
        SELECT
          season, contestant_id, posted_date AS feature_date, source,
          COUNT(*) AS mention_volume,
          AVG(sentiment * confidence) AS sentiment_mean,
          SUM(sentiment * confidence * CASE WHEN engagement > 0 THEN engagement ELSE 1 END) AS weighted_sum,
          SUM(CASE WHEN engagement > 0 THEN engagement ELSE 1 END) AS engagement_total
        FROM contestant_mentions
        WHERE season = ?
        GROUP BY season, contestant_id, posted_date, source
        """,
        (season,),
    )
    rows = []
    for row in mention_rows:
        engagement_total = float(row["engagement_total"] or 0)
        weighted = float(row["weighted_sum"] or 0)
        rows.append(
            {
                "season": row["season"],
                "contestant_id": row["contestant_id"],
                "feature_date": row["feature_date"],
                "source": row["source"],
                "mention_volume": row["mention_volume"],
                "sentiment_mean": float(row["sentiment_mean"] or 0),
                "engagement_weighted_sentiment": weighted / engagement_total if engagement_total else 0,
                "engagement_total": engagement_total,
                "source_available": 1,
            }
        )
    replace_daily_source_metrics(database_path, rows)
    return len(rows)


def build_features_and_predictions(database_path, season: int, feature_date: date, day: int) -> FeatureBuildResult:
    metric_count = build_daily_source_metrics(database_path, season)
    contestants = active_contestants(season, day)
    feature_rows = build_feature_rows(database_path, season, feature_date, day, contestants)
    replace_model_features(database_path, feature_rows)
    prediction_rows = build_prediction_rows(feature_rows, contestants)
    replace_predictions(database_path, prediction_rows)
    return FeatureBuildResult(metric_count, len(feature_rows), len(prediction_rows))


def build_feature_rows(database_path, season: int, feature_date: date, day: int, contestants: tuple[Contestant, ...]) -> list[dict]:
    source_lookup = load_source_lookup(database_path, season, feature_date, days=7)
    manual_tiktok = load_manual_tiktok(database_path, feature_date)
    manual_episode = load_manual_episode(database_path, feature_date)
    rows = []
    for contestant in contestants:
        availability = {source: False for source in ALL_SOURCES}
        reddit_today = source_value(source_lookup, contestant.id, feature_date, "reddit")
        twitter_today = source_value(source_lookup, contestant.id, feature_date, "twitter")
        reddit_score = reddit_today
        twitter_score = twitter_today
        availability["reddit"] = reddit_today is not None
        availability["twitter"] = twitter_today is not None

        tiktok_score = manual_tiktok.get(contestant.id)
        personal_score = manual_episode.get(contestant.id)
        availability["tiktok"] = tiktok_score is not None
        availability["personal"] = personal_score is not None
        availability["episode"] = personal_score is not None
        show_prior = show_prior_score(season, contestant.id, day)
        availability["show"] = show_prior != 0

        rows.append(
            {
                "season": season,
                "contestant_id": contestant.id,
                "feature_date": feature_date.isoformat(),
                "day": day,
                "reddit_score": reddit_score,
                "twitter_score": twitter_score,
                "trends_score": None,
                "tiktok_score": tiktok_score,
                "episode_score": personal_score,
                "personal_score": personal_score,
                "show_prior_score": show_prior,
                "social_3d_score": rolling_social_score(source_lookup, contestant.id, feature_date, 3),
                "social_7d_score": rolling_social_score(source_lookup, contestant.id, feature_date, 7),
                "source_availability_json": json.dumps(availability, sort_keys=True),
            }
        )
    return rows


def build_prediction_rows(feature_rows: list[dict], contestants: tuple[Contestant, ...]) -> list[dict]:
    contestant_lookup = {contestant.id: contestant for contestant in contestants}
    scored = []
    for row in feature_rows:
        source_breakdown = {
            "reddit": row["reddit_score"],
            "twitter": row["twitter_score"],
            "trends": row["trends_score"],
            "tiktok": row["tiktok_score"],
            "episode": row["episode_score"],
            "personal": row["personal_score"],
            "show": row["show_prior_score"],
            "social3d": row["social_3d_score"],
            "social7d": row["social_7d_score"],
        }
        score = weighted_score(row)
        scored.append((row, source_breakdown, score))
    raw = [math.exp(score * 2.4) for _, _, score in scored]
    total = sum(raw) or 1
    prediction_rows = []
    for index, (row, source_breakdown, score) in enumerate(scored):
        contestant = contestant_lookup[row["contestant_id"]]
        prediction_rows.append(
            {
                "season": row["season"],
                "contestant_id": row["contestant_id"],
                "feature_date": row["feature_date"],
                "day": row["day"],
                "score": score,
                "probability": raw[index] / total,
                "source_breakdown_json": json.dumps(source_breakdown, sort_keys=True),
                "source_availability_json": row["source_availability_json"],
                "display_name": contestant.display_name,
                "gender": contestant.gender,
            }
        )
    return prediction_rows


def weighted_score(row: dict) -> float:
    score = 0.0
    current_social = mean_present([row["reddit_score"], row["twitter_score"]])
    blended_social = mean_present([current_social, row["social_3d_score"]])
    if blended_social is not None:
        score += blended_social * 0.18
    score += float(row["social_3d_score"]) * 0.16
    score += float(row["social_7d_score"]) * 0.08
    score += float(row["show_prior_score"]) * 0.72
    for optional_key in ("tiktok_score", "episode_score", "personal_score"):
        value = row[optional_key]
        if value is not None:
            score += float(value) * 0.10
    return score


def show_prior_score(season: int, contestant_id: str, day: int) -> float:
    config = load_show_prior_config(season)
    if day < int(config.get("effectiveFromDay", 999)):
        return 0.0
    return float(config.get("priors", {}).get(contestant_id, 0.0))


@lru_cache(maxsize=8)
def load_show_prior_config(season: int) -> dict:
    path = Path("data") / "config" / f"show_priors.season{season}.json"
    if not path.exists():
        return {"effectiveFromDay": 999, "priors": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def load_source_lookup(database_path, season: int, feature_date: date, days: int):
    start_date = (feature_date - timedelta(days=days - 1)).isoformat()
    rows = fetch_all(
        database_path,
        """
        SELECT contestant_id, feature_date, source, engagement_weighted_sentiment, sentiment_mean, source_available
        FROM daily_source_metrics
        WHERE season = ? AND feature_date BETWEEN ? AND ?
        """,
        (season, start_date, feature_date.isoformat()),
    )
    lookup = {}
    for row in rows:
        value = row["engagement_weighted_sentiment"] if row["engagement_weighted_sentiment"] is not None else row["sentiment_mean"]
        lookup[(row["contestant_id"], row["feature_date"], row["source"])] = float(value or 0)
    return lookup


def source_value(source_lookup, contestant_id: str, feature_date: date, source: str) -> float | None:
    return source_lookup.get((contestant_id, feature_date.isoformat(), source))


def rolling_social_score(source_lookup, contestant_id: str, feature_date: date, days: int) -> float:
    values = []
    for offset in range(days):
        current = (feature_date - timedelta(days=offset)).isoformat()
        for source in SOCIAL_SOURCES:
            value = source_lookup.get((contestant_id, current, source))
            if value is not None:
                values.append(value)
    return sum(values) / len(values) if values else 0.0


def load_manual_tiktok(database_path, feature_date: date) -> dict[str, float]:
    rows = fetch_all(
        database_path,
        """
        SELECT contestant_id, positive_sentiment, visible_edit_volume, comment_tone, viral_momentum
        FROM manual_tiktok_entries
        WHERE feature_date = ?
        """,
        (feature_date.isoformat(),),
    )
    scores: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        polarity = 0.35 if row["positive_sentiment"] else -0.35
        score = polarity + (row["visible_edit_volume"] - 3) * 0.11 + (row["comment_tone"] - 3) * 0.13 + (row["viral_momentum"] - 3) * 0.12
        scores[row["contestant_id"]].append(score)
    return {contestant_id: sum(values) / len(values) for contestant_id, values in scores.items()}


def load_manual_episode(database_path, feature_date: date) -> dict[str, float]:
    rows = fetch_all(
        database_path,
        """
        SELECT contestant_id, episode_enjoyment, got_good_edit, relationship_strength, risk_of_dumping
        FROM manual_episode_entries
        WHERE feature_date = ?
        """,
        (feature_date.isoformat(),),
    )
    scores: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        edit = 0.25 if row["got_good_edit"] else -0.12
        score = edit + (row["episode_enjoyment"] - 3) * 0.10 + (row["relationship_strength"] - 3) * 0.16 - (row["risk_of_dumping"] - 3) * 0.18
        scores[row["contestant_id"]].append(score)
    return {contestant_id: sum(values) / len(values) for contestant_id, values in scores.items()}


def mean_present(values: list[float | None]) -> float | None:
    present = [float(value) for value in values if value is not None]
    return sum(present) / len(present) if present else None
