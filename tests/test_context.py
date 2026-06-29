from islandedge.context import match_mentions
from islandedge.contestants import contestants_for_season


def test_name_mentions_need_love_island_context_for_common_first_names():
    contestants = contestants_for_season(8)

    assert match_mentions("Bryce is funny at work", contestants) == []

    matches = match_mentions("Bryce is my Love Island USA favorite", contestants)
    assert [match.contestant_id for match in matches] == ["s8-bryce"]
    assert matches[0].confidence == 1.0


def test_tierra_matches_titi_alias():
    contestants = contestants_for_season(8)
    matches = match_mentions("Tierra is running the villa on Love Island", contestants)

    assert [match.contestant_id for match in matches] == ["s8-titi"]
