"""Generate an iCalendar feed from the selected OV Helsingborg home matches."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .filtering import CompetitionMatch, OV_HELSINGBORG_HK


CALENDAR_NAME = "OV Helsingborg Herr – Hemmamatcher"
CALENDAR_TIMEZONE = "Europe/Stockholm"
MATCH_DURATION = timedelta(hours=2)
_SWEDISH_MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "maj": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "okt": 10,
    "nov": 11,
    "dec": 12,
}


def render_calendar(
    matches: list[CompetitionMatch], generated_at: datetime | None = None
) -> str:
    """Render selected OV home matches as a UTF-8 iCalendar document."""
    timestamp = generated_at or datetime.now(timezone.utc)
    timestamp = timestamp.astimezone(timezone.utc)
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
        "PRODID:-//pj-franck//OV Helsingborg Herr Calendar//SV",
        f"X-WR-CALNAME:{_escape(CALENDAR_NAME)}",
        f"X-WR-TIMEZONE:{CALENDAR_TIMEZONE}",
    ]

    for competition_match in matches:
        match = competition_match.match
        if match.home_team != OV_HELSINGBORG_HK:
            raise ValueError("Kalendern får endast innehålla OV Helsingborgs hemmamatcher.")
        start = _match_start(match.date, match.time)
        end = start + MATCH_DURATION
        opponent = match.away_team
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{match.match_id}@ov-hbg-herr-cal",
                f"DTSTAMP:{timestamp.strftime('%Y%m%dT%H%M%SZ')}",
                f"DTSTART;TZID={CALENDAR_TIMEZONE}:{start.strftime('%Y%m%dT%H%M%S')}",
                f"DTEND;TZID={CALENDAR_TIMEZONE}:{end.strftime('%Y%m%dT%H%M%S')}",
                f"SUMMARY:{_escape(f'🤾 OV Helsingborg – {opponent}')}",
            ]
        )
        if match.venue:
            lines.append(f"LOCATION:{_escape(match.venue)}")
        lines.extend(
            [
                f"DESCRIPTION:{_escape(match.notes or '')}",
                f"URL:{_escape(match.source_url)}",
                "END:VEVENT",
            ]
        )

    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold(line) for line in lines) + "\r\n"


def _match_start(date: str, time: str | None) -> datetime:
    """Parse Profixio's Swedish date and time fields in the Stockholm timezone."""
    try:
        day, month_name, year = date.lower().split()
        hour, minute = (time or "00:00").split(":")
        return datetime(int(year), _SWEDISH_MONTHS[month_name], int(day), int(hour), int(minute))
    except (KeyError, ValueError) as error:
        raise ValueError(f"Ogiltigt matchdatum från Profixio: {date!r} {time!r}") from error


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _fold(line: str) -> str:
    """Fold long iCalendar content lines at 75 UTF-8 octets."""
    chunks: list[str] = []
    chunk = ""
    limit = 75
    for character in line:
        if len((chunk + character).encode("utf-8")) > limit:
            chunks.append(chunk)
            chunk = " " + character
            limit = 74
        else:
            chunk += character
    chunks.append(chunk)
    return "\r\n".join(chunks)
