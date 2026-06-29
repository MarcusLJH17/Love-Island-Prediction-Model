from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureRow:
    contestant_name: str
    reddit: float
    twitter: float
    trends: float
    tiktok: float
    episode: float
    personal: float
    days_in_villa: int
    is_og: bool


WEIGHTS = {
    "reddit": 0.23,
    "twitter": 0.18,
    "trends": 0.16,
    "tiktok": 0.18,
    "episode": 0.15,
    "personal": 0.10,
}


def sigmoid(value: float) -> float:
    return 1 / (1 + math.exp(-value))


def score_row(row: FeatureRow, enabled_sources: dict[str, bool] | None = None) -> float:
    enabled = enabled_sources or {source: True for source in WEIGHTS}
    score = 0.0
    for source, weight in WEIGHTS.items():
        if enabled.get(source, False):
            score += getattr(row, source) * weight
    score += min(0.4, row.days_in_villa * 0.012)
    score += 0.05 if row.is_og else 0
    return score


def probability_distribution(rows: list[FeatureRow], enabled_sources: dict[str, bool] | None = None) -> dict[str, float]:
    raw = {row.contestant_name: sigmoid(score_row(row, enabled_sources)) for row in rows}
    total = sum(raw.values()) or 1
    return {name: value / total for name, value in raw.items()}
