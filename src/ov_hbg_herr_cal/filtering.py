"""Select the matches that belong in OV Helsingborg's home-match calendar."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable

from .source import Match


OV_HELSINGBORG_HK = "OV Helsingborg HK"
HANDBOLLSLIGAN = "Handbollsligan herr"
SVENSKA_CUPEN = "Svenska cupen"
ALLOWED_COMPETITIONS = frozenset({HANDBOLLSLIGAN, SVENSKA_CUPEN})


@dataclass(frozen=True)
class CompetitionMatch:
    """A Profixio match together with the competition it belongs to."""

    competition: str
    match: Match


def select_ov_home_matches(matches: Iterable[CompetitionMatch]) -> list[CompetitionMatch]:
    """Return OV's home matches in Handbollsligan or Svenska Cupen only."""
    return [
        competition_match
        for competition_match in matches
        if competition_match.competition in ALLOWED_COMPETITIONS
        and competition_match.match.home_team == OV_HELSINGBORG_HK
    ]
