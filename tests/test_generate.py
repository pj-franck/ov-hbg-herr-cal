from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from ov_hbg_herr_cal.generate import calendar_from_league_matches
from ov_hbg_herr_cal.source import Match


class GenerateTests(unittest.TestCase):
    def test_generates_only_home_matches(self) -> None:
        home = Match("1", "22 sep 2026", "19:00", "OV Helsingborg HK", "IF Hallby HK", "Helsingborg Arena", "https://example.test/1")
        away = Match("2", "29 sep 2026", "19:00", "IF Hallby HK", "OV Helsingborg HK", "Jönköpings Idrottshus", "https://example.test/2")

        calendar = calendar_from_league_matches([home, away])

        self.assertEqual(calendar.count("BEGIN:VEVENT"), 1)
        self.assertIn("UID:1@ov-hbg-herr-cal", calendar)
        self.assertNotIn("UID:2@ov-hbg-herr-cal", calendar)


if __name__ == "__main__":
    unittest.main()
