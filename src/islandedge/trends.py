from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable

from islandedge.contestants import Contestant


ANCHOR_TERM = "Love Island USA"


def trend_query(contestant: Contestant) -> str:
    if contestant.id == "s8-titi":
        return "Tierra Love Island"
    name = contestant.full_name if " " in contestant.full_name else contestant.display_name
    return f"{name} Love Island"


def trend_batches(contestants: Iterable[Contestant], batch_size: int = 4) -> list[list[Contestant]]:
    ordered = list(contestants)
    return [ordered[index : index + batch_size] for index in range(0, len(ordered), batch_size)]


def collect_trend_interest(contestants: Iterable[Contestant], feature_date: date, geo: str = "US") -> dict[str, float]:
    try:
        from pytrends.request import TrendReq
    except ImportError as error:
        raise RuntimeError("pytrends is not installed. Run `python -m pip install -r requirements.txt`.") from error

    start_date = feature_date - timedelta(days=7)
    end_date = feature_date + timedelta(days=1)
    timeframe = f"{start_date.isoformat()} {end_date.isoformat()}"
    pytrends = TrendReq(hl="en-US", tz=360)
    interest: dict[str, float] = {}

    for batch in trend_batches(contestants):
        terms = [trend_query(contestant) for contestant in batch]
        keywords = [*terms, ANCHOR_TERM]
        pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo, gprop="")
        frame = pytrends.interest_over_time()
        if frame.empty:
            continue
        if "isPartial" in frame.columns:
            frame = frame.drop(columns=["isPartial"])
        eligible = frame[frame.index.date <= feature_date]
        if eligible.empty:
            continue
        latest = eligible.iloc[-1]
        anchor = max(float(latest.get(ANCHOR_TERM, 0) or 0), 1.0)
        for contestant, term in zip(batch, terms):
            value = float(latest.get(term, 0) or 0)
            interest[contestant.id] = max(interest.get(contestant.id, 0.0), value / anchor)

    return interest


def trend_metric_rows(season: int, feature_date: date, interest: dict[str, float]) -> list[dict]:
    max_interest = max(interest.values(), default=0.0)
    rows = []
    for contestant_id, value in interest.items():
        signal = value / max_interest if max_interest > 0 else 0.0
        rows.append(
            {
                "season": season,
                "contestant_id": contestant_id,
                "feature_date": feature_date.isoformat(),
                "source": "trends",
                "mention_volume": int(round(value * 100)),
                "sentiment_mean": signal,
                "engagement_weighted_sentiment": signal,
                "engagement_total": value,
                "source_available": 1,
            }
        )
    return rows
