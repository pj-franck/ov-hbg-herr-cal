"""Create the published OV Helsingborg home-match iCalendar feed."""

from __future__ import annotations

import argparse
from pathlib import Path

from .calendar import render_calendar
from .filtering import CompetitionMatch, HANDBOLLSLIGAN, select_ov_home_matches
from .source import Match, ProfixioSource


def calendar_from_league_matches(matches: list[Match]) -> str:
    """Turn the official league schedule into the current published calendar."""
    competition_matches = [CompetitionMatch(HANDBOLLSLIGAN, match) for match in matches]
    return render_calendar(select_ov_home_matches(competition_matches))


def write_calendar(output_path: Path) -> int:
    """Fetch the official schedule and write the selected home matches to disk."""
    calendar = calendar_from_league_matches(ProfixioSource().fetch_matches())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(calendar, encoding="utf-8", newline="")
    return calendar.count("BEGIN:VEVENT")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate OV Helsingborg's home-match calendar.")
    parser.add_argument("--output", type=Path, required=True, help="Path for the generated .ics file")
    arguments = parser.parse_args()
    count = write_calendar(arguments.output)
    print(f"Wrote {count} OV Helsingborg home matches to {arguments.output}")


if __name__ == "__main__":
    main()
