from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Contestant:
    id: str
    display_name: str
    full_name: str
    gender: str
    entered_day: int
    exit_day: int | None
    aliases: tuple[str, ...]


SEASON8_CONTESTANTS: tuple[Contestant, ...] = (
    Contestant("s8-aniya", "Aniya", "Aniya Harvey", "woman", 1, None, ("aniya", "aniya harvey")),
    Contestant("s8-beatriz", "Beatriz", "Beatriz", "woman", 1, 9, ("beatriz",)),
    Contestant("s8-bryce", "Bryce", "Bryce Dettloff", "man", 1, None, ("bryce", "bryce dettloff")),
    Contestant("s8-kc", "KC", "KC Chandler", "man", 1, 40, ("kc", "k c", "kc chandler")),
    Contestant("s8-kenzie", "Kenzie", "Kenzie Annis", "woman", 1, 40, ("kenzie", "kenzie annis")),
    Contestant("s8-melanie", "Melanie", "Melanie Moreno", "woman", 1, None, ("melanie", "melanie moreno")),
    Contestant("s8-sean", "Sean", "Sean", "man", 1, 5, ("sean",)),
    Contestant("s8-sincere", "Sincere", "Sincere Rhea", "man", 1, None, ("sincere", "sincere rhea")),
    Contestant("s8-trinity", "Trinity", "Trinity Tatum", "woman", 1, None, ("trinity", "trinity tatum")),
    Contestant("s8-zach", "Zach", "Zach Georgiou", "man", 1, None, ("zach", "zach georgiou")),
    Contestant("s8-gabriel", "Gabriel", "Gabriel", "man", 2, 14, ("gabriel",)),
    Contestant("s8-kayda", "Kayda", "Kayda Bosse", "woman", 2, None, ("kayda", "kayda bosse")),
    Contestant("s8-corbin", "Corbin", "Corbin Mims", "man", 4, 40, ("corbin", "corbin mims")),
    Contestant("s8-caleb", "Caleb", "Caleb McDaniel", "man", 6, 32, ("caleb", "caleb mcdaniel")),
    Contestant("s8-jen", "Jen", "Jen Terry", "woman", 6, 32, ("jen", "jennifer", "jen terry")),
    Contestant("s8-sol", "Sol", "Sol", "woman", 6, 14, ("sol",)),
    Contestant("s8-amora", "Amora", "Amora Cachee", "woman", 20, 32, ("amora", "amora cachee")),
    Contestant("s8-jaiden", "Jaiden", "Jaiden Bacciocco", "woman", 20, 32, ("jaiden", "jaiden bacciocco")),
    Contestant("s8-parmida", "Parmida", "Parmida", "woman", 20, 40, ("parmida",)),
    Contestant("s8-sydney", "Sydney", "Sydney Eugene", "woman", 20, 24, ("sydney", "sydney eugene")),
    Contestant("s8-titi", "Titi", "Titi", "woman", 20, 40, ("titi", "tierra")),
    Contestant("s8-carl", "Carl", "Carl Lee Schmidt", "man", 24, None, ("carl", "carl lee", "carl schmidt")),
    Contestant("s8-chandlar", "Chandlar", "Chandlar Wilson", "man", 24, 24, ("chandlar", "chandlar wilson")),
    Contestant("s8-chay", "Chay", "Chay Nehra", "man", 24, 24, ("chay", "chay nehra")),
    Contestant("s8-corey", "Corey", "Corey Sawyer Jr.", "man", 24, 24, ("corey", "corey sawyer")),
    Contestant("s8-dylan", "Dylan", "Dylan Wrona", "man", 24, 40, ("dylan", "dylan wrona")),
    Contestant("s8-gal", "Gal", "Gal Tshnieder", "man", 24, 32, ("gal", "gal tshnieder")),
    Contestant("s8-keyon", "Keyon", "Keyon Harry", "man", 24, 24, ("keyon", "keyon harry")),
    Contestant("s8-kyle", "Kyle", "Kyle Greene", "man", 24, 24, ("kyle", "kyle greene")),
    Contestant("s8-ronnie", "Ronnie", "Ronnie Gunter", "man", 24, 24, ("ronnie", "ronnie gunter")),
    Contestant("s8-ryan", "Ryan", "Ryan Ten Hulscher", "man", 24, 24, ("ryan", "ryan ten hulscher")),
    Contestant("s8-tino", "Tino", "Tino Ellis", "man", 24, 24, ("tino", "tino ellis")),
    Contestant("s8-trae", "Trae", "Trae Taylor", "man", 24, 24, ("trae", "trae taylor")),
)


def contestants_for_season(season: int) -> tuple[Contestant, ...]:
    if season != 8:
        raise ValueError("Only Season 8 scraping metadata is implemented.")
    return SEASON8_CONTESTANTS


def active_contestants(season: int, day: int) -> tuple[Contestant, ...]:
    return tuple(
        contestant
        for contestant in contestants_for_season(season)
        if contestant.entered_day <= day and (contestant.exit_day is None or contestant.exit_day >= day)
    )
