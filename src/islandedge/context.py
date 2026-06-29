from __future__ import annotations

import re
from dataclasses import dataclass

from islandedge.contestants import Contestant


SHOW_CONTEXT_TERMS = {
    "love island",
    "love island usa",
    "liusa",
    "villa",
    "recoupling",
    "couple",
    "coupled",
    "dumped",
    "dumping",
    "bombshell",
    "casa",
    "casa amor",
    "islander",
    "islanders",
    "peacock",
    "episode",
}

POSITIVE_TERMS = {
    "favorite",
    "favourite",
    "love",
    "loved",
    "cute",
    "chemistry",
    "rooting",
    "winner",
    "strong",
    "best",
    "genuine",
    "funny",
    "icon",
    "queen",
    "king",
}

NEGATIVE_TERMS = {
    "hate",
    "hated",
    "annoying",
    "fake",
    "boring",
    "dump",
    "dumped",
    "toxic",
    "messy",
    "bad",
    "worst",
    "cringe",
    "villain",
    "red flag",
}


@dataclass(frozen=True)
class MentionMatch:
    contestant_id: str
    alias: str
    confidence: float
    sentiment: float
    context_terms: tuple[str, ...]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def has_alias(text: str, alias: str) -> bool:
    pattern = r"(?<![a-z0-9])" + re.escape(alias.lower()) + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None


def context_terms(text: str) -> tuple[str, ...]:
    normalized = normalize_text(text)
    return tuple(term for term in sorted(SHOW_CONTEXT_TERMS) if term in normalized)


def sentiment_score(text: str) -> float:
    normalized = normalize_text(text)
    positive = sum(1 for term in POSITIVE_TERMS if term in normalized)
    negative = sum(1 for term in NEGATIVE_TERMS if term in normalized)
    total = positive + negative
    if total == 0:
        return 0.0
    return max(-1.0, min(1.0, (positive - negative) / total))


def match_mentions(text: str, contestants: tuple[Contestant, ...]) -> list[MentionMatch]:
    normalized = normalize_text(text)
    terms = context_terms(normalized)
    matches: list[MentionMatch] = []
    for contestant in contestants:
        matched_alias = next((alias for alias in contestant.aliases if has_alias(normalized, alias)), None)
        if matched_alias is None:
            continue
        direct_show_context = bool(terms)
        full_name_match = " " in matched_alias
        confidence = 1.0 if direct_show_context else 0.55 if full_name_match else 0.25
        if confidence < 0.5:
            continue
        matches.append(
            MentionMatch(
                contestant_id=contestant.id,
                alias=matched_alias,
                confidence=confidence,
                sentiment=sentiment_score(normalized),
                context_terms=terms,
            )
        )
    return matches
