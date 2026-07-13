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
    Contestant("s8-beatriz", "Beatriz", "Beatriz Hatz", "woman", 1, 10, ("beatriz", "beatriz hatz")),
    Contestant("s8-bryce", "Bryce", "Bryce Dettloff", "man", 1, None, ("bryce", "bryce dettloff")),
    Contestant("s8-kc", "KC", "KC Chandler", "man", 1, 39, ("kc", "k c", "kc chandler")),
    Contestant("s8-kenzie", "Kenzie", "Kenzie Annis", "woman", 1, 39, ("kenzie", "kenzie annis")),
    Contestant("s8-melanie", "Melanie", "Melanie Moreno", "woman", 1, None, ("melanie", "melanie moreno")),
    Contestant("s8-sean", "Sean", "Sean Reifel", "man", 1, 6, ("sean", "sean reifel")),
    Contestant("s8-sincere", "Sincere", "Sincere Rhea", "man", 1, None, ("sincere", "sincere rhea")),
    Contestant("s8-trinity", "Trinity", "Trinity Tatum", "woman", 1, None, ("trinity", "trinity tatum")),
    Contestant("s8-zach", "Zach", "Zach Georgiou", "man", 1, None, ("zach", "zach georgiou")),
    Contestant("s8-gabriel", "Gabriel", "Gabriel Vasconcelos", "man", 2, 14, ("gabriel", "gabriel vasconcelos")),
    Contestant("s8-kayda", "Kayda", "Kayda Bosse", "woman", 2, None, ("kayda", "kayda bosse")),
    Contestant("s8-corbin", "Corbin", "Corbin Mims", "man", 4, 34, ("corbin", "corbin mims")),
    Contestant("s8-caleb", "Caleb", "Caleb McDaniel", "man", 6, 32, ("caleb", "caleb mcdaniel")),
    Contestant("s8-jen", "Jen", "Jen Terry", "woman", 6, 32, ("jen", "jennifer", "jen terry")),
    Contestant("s8-sol", "Sol", "Sol Dean", "woman", 6, 14, ("sol", "sol dean")),
    Contestant("s8-amora", "Amora", "Amora Cachee Robinson", "woman", 20, 32, ("amora", "amora cachee", "amora robinson")),
    Contestant("s8-alannah", "Alannah", "Alannah Keyser", "woman", 20, 23, ("alannah", "alannah keyser")),
    Contestant("s8-jaiden", "Jaiden", "Jaiden Bacciocco", "woman", 20, 32, ("jaiden", "jaiden bacciocco")),
    Contestant("s8-parmida", "Parmida", "Parmida Keshani", "woman", 20, 34, ("parmida", "parmida keshani")),
    Contestant("s8-sydney", "Sydney", "Sydney Eugene", "woman", 20, 24, ("sydney", "sydney eugene")),
    Contestant("s8-titi", "Titi", "Tierra Davis", "woman", 20, 39, ("titi", "tierra", "tierra davis")),
    Contestant("s8-carl", "Carl", "Carl Lee Schmidt", "man", 24, None, ("carl", "carl lee", "carl schmidt")),
    Contestant("s8-chandlar", "Chandlar", "Chandlar Wilson", "man", 24, 24, ("chandlar", "chandlar wilson")),
    Contestant("s8-chay", "Chay", "Chay Nehra", "man", 24, 24, ("chay", "chay nehra")),
    Contestant("s8-corey", "Corey", "Corey Sawyer Jr.", "man", 24, 24, ("corey", "corey sawyer")),
    Contestant("s8-dylan", "Dylan", "Dylan Wrona", "man", 24, 39, ("dylan", "dylan wrona")),
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
