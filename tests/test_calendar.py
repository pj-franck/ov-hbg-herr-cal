from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from ov_hbg_herr_cal.calendar import render_calendar
from ov_hbg_herr_cal.filtering import CompetitionMatch, HANDBOLLSLIGAN
from ov_hbg_herr_cal.source import Match


class CalendarTests(unittest.TestCase):
    def test_renders_a_stockholm_home_match(self) -> None:
        match = Match(
            match_id="12345",
            date="22 sep 2026",
            time="19:00",
            home_team="OV Helsingborg HK",
            away_team="IF Hallby HK",
            venue="Idrottens Hus Helsingborg",
            source_url="https://example.test/match/12345",
        )

        calendar = render_calendar(
            [CompetitionMatch(HANDBOLLSLIGAN, match)],
            generated_at=datetime(2026, 8, 8, 10, 0, tzinfo=timezone.utc),
        )

        self.assertTrue(calendar.startswith("BEGIN:VCALENDAR\r\n"))
        self.assertIn("DTSTART;TZID=Europe/Stockholm:20260922T190000", calendar)
        self.assertIn("DTEND;TZID=Europe/Stockholm:20260922T210000", calendar)
        self.assertIn("SUMMARY:🤾 OV Helsingborg – IF Hallby HK", calendar)
        self.assertIn("LOCATION:Idrottens Hus Helsingborg", calendar)
        self.assertIn("UID:12345@ov-hbg-herr-cal", calendar)
        self.assertIn("DTSTAMP:20260808T100000Z", calendar)
        self.assertTrue(calendar.endswith("END:VCALENDAR\r\n"))

    def test_rejects_an_away_match(self) -> None:
        match = Match("1", "22 sep 2026", "19:00", "IF Hallby HK", "OV Helsingborg HK", None, "https://example.test")

        with self.assertRaises(ValueError):
            render_calendar([CompetitionMatch(HANDBOLLSLIGAN, match)])

    def test_uses_helsingborg_arena_when_the_source_has_no_venue(self) -> None:
        match = Match("2", "22 sep 2026", "19:00", "OV Helsingborg HK", "IF Hallby HK", None, "https://example.test")

        calendar = render_calendar([CompetitionMatch(HANDBOLLSLIGAN, match)])

        self.assertIn("LOCATION:Helsingborg Arena", calendar)


if __name__ == "__main__":
    unittest.main()
