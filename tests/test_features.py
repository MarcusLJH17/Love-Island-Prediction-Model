from datetime import date

from islandedge.contestants import active_contestants, contestants_for_season
from islandedge.features import build_feature_rows, build_features_and_predictions
from islandedge.ingest import extract_mentions
from islandedge.storage import insert_mentions, insert_raw_posts, upsert_contestants


def test_missing_manual_signals_remain_unknown_not_negative(tmp_path):
    db = tmp_path / "islandedge.sqlite"
    contestants = active_contestants(8, 28)
    upsert_contestants(db, 8, contestants_for_season(8))

    rows = build_feature_rows(db, 8, date(2026, 6, 29), 28, contestants)
    bryce = next(row for row in rows if row["contestant_id"] == "s8-bryce")

    assert bryce["tiktok_score"] is None
    assert bryce["personal_score"] is None
    assert bryce["social_3d_score"] == 0.0


def test_build_predictions_from_social_mentions(tmp_path):
    db = tmp_path / "islandedge.sqlite"
    contestants = active_contestants(8, 28)
    upsert_contestants(db, 8, contestants_for_season(8))
    raw_posts = [
        {
            "id": "post-1",
            "season": 8,
            "source": "reddit",
            "source_id": "post-1",
            "source_url": None,
            "author": "tester",
            "text": "Bryce and Trinity are Love Island favorites with winner chemistry.",
            "posted_at": "2026-06-29T12:00:00",
            "query": "sample",
            "subreddit": "LoveIslandUSA",
            "engagement": 10,
        }
    ]
    insert_raw_posts(db, raw_posts)
    insert_mentions(db, extract_mentions(raw_posts, contestants))

    result = build_features_and_predictions(db, 8, date(2026, 6, 29), 28)

    assert result.metric_rows == 2
    assert result.feature_rows == len(contestants)
    assert result.prediction_rows == len(contestants)
