import json

from islandedge.export import export_predictions
from islandedge.storage import replace_predictions


def prediction_row(contestant_id: str, probability: float) -> dict:
    return {
        "season": 8,
        "contestant_id": contestant_id,
        "feature_date": "2026-07-07",
        "day": 36,
        "score": probability,
        "probability": probability,
        "source_breakdown_json": "{}",
        "source_availability_json": "{}",
    }


def test_export_filters_post_exit_predictions_and_renormalizes(tmp_path):
    db = tmp_path / "islandedge.sqlite"
    out = tmp_path / "season8_daily.json"
    replace_predictions(
        db,
        [
            prediction_row("s8-bryce", 0.4),
            prediction_row("s8-trinity", 0.4),
            prediction_row("s8-corbin", 0.2),
        ],
    )

    payload = export_predictions(db, 8, out)
    contestants = payload["days"][0]["contestants"]

    assert [contestant["id"] for contestant in contestants] == ["s8-bryce", "s8-trinity"]
    assert sum(contestant["probability"] for contestant in contestants) == 1.0
    assert json.loads(out.read_text(encoding="utf-8"))["days"][0]["contestants"] == contestants
