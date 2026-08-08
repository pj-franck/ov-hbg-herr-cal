from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from ov_hbg_herr_cal.source import DEFAULT_LEAGUE_SCHEDULE_URL, _livewire_metadata, parse_matches


class ParseMatchesTests(unittest.TestCase):
    def setUp(self) -> None:
        fixture = Path(__file__).parent / "fixtures" / "profixio_schedule.html"
        self.html = fixture.read_text(encoding="utf-8")

    def test_parses_all_rendered_matches(self) -> None:
        matches = parse_matches(self.html, "https://example.test/schedule")

        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0].home_team, "Ystads IF HF")
        self.assertEqual(matches[0].away_team, "OV Helsingborg HK")
        self.assertEqual(matches[0].venue, "Ystad Arena")
        self.assertEqual(matches[1].match_id, "1002")
        self.assertEqual(matches[1].date, "22 sep 2025")
        self.assertEqual(matches[1].time, "19:00")

    def test_reads_livewire_metadata(self) -> None:
        html = '<div wire:key="x-schedule-0" wire:snapshot="{&quot;id&quot;:1}"></div><script data-csrf="token"></script>'

        self.assertEqual(_livewire_metadata(html), ('{"id":1}', "token"))

    def test_defaults_to_the_2026_27_league_schedule(self) -> None:
        self.assertIn("leagueid28137", DEFAULT_LEAGUE_SCHEDULE_URL)
        self.assertIn("teams/1584193", DEFAULT_LEAGUE_SCHEDULE_URL)


if __name__ == "__main__":
    unittest.main()
