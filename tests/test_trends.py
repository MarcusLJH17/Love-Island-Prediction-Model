from datetime import date

from islandedge.contestants import SEASON8_CONTESTANTS
from islandedge.trends import trend_metric_rows, trend_query


def test_titi_trend_query_uses_nickname_context():
    titi = next(contestant for contestant in SEASON8_CONTESTANTS if contestant.id == "s8-titi")

    assert trend_query(titi) == "Tierra Love Island"


def test_trend_metric_rows_normalize_interest():
    rows = trend_metric_rows(
        8,
        date(2026, 7, 1),
        {"s8-trinity": 1.0, "s8-bryce": 0.5},
    )

    by_id = {row["contestant_id"]: row for row in rows}
    assert by_id["s8-trinity"]["source"] == "trends"
    assert by_id["s8-trinity"]["sentiment_mean"] == 1.0
    assert by_id["s8-bryce"]["sentiment_mean"] == 0.5
    assert by_id["s8-trinity"]["source_available"] == 1
