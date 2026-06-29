from datetime import date

from islandedge.contestants import active_contestants, contestants_for_season
from islandedge.features import build_feature_rows, build_features_and_predictions
from islandedge.ingest import extract_mentions
from islandedge.storage import insert_mentions, insert_raw_posts, upsert_contestants
from islandedge.storage import fetch_all, replace_predictions


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


def test_post_casa_priors_anchor_current_favorites(tmp_path):
    db = tmp_path / "islandedge.sqlite"
    contestants = active_contestants(8, 28)
    upsert_contestants(db, 8, contestants_for_season(8))

    rows = build_feature_rows(db, 8, date(2026, 6, 29), 28, contestants)
    by_id = {row["contestant_id"]: row for row in rows}

    assert by_id["s8-bryce"]["show_prior_score"] > 0.8
    assert by_id["s8-trinity"]["show_prior_score"] > 0.8
    assert by_id["s8-aniya"]["show_prior_score"] > 0.4
    assert by_id["s8-carl"]["show_prior_score"] > 0.4
    assert "s8-corey" not in by_id
    assert "s8-chay" not in by_id


def test_prediction_replacement_removes_stale_rows(tmp_path):
    db = tmp_path / "islandedge.sqlite"
    stale = {
        "season": 8,
        "contestant_id": "s8-corey",
        "feature_date": "2026-06-29",
        "day": 28,
        "score": 1,
        "probability": 1,
        "source_breakdown_json": "{}",
        "source_availability_json": "{}",
    }
    fresh = {**stale, "contestant_id": "s8-bryce", "score": 2}

    replace_predictions(db, [stale])
    replace_predictions(db, [fresh])
    rows = fetch_all(db, "SELECT contestant_id FROM predictions WHERE season = 8 AND feature_date = '2026-06-29'")

    assert [row["contestant_id"] for row in rows] == ["s8-bryce"]
