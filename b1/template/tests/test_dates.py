import datetime
import unittest
from minishop.dates import parse_jp_date


class TestDates(unittest.TestCase):
    def test_kanji(self):
        self.assertEqual(parse_jp_date("2026年3月4日"), datetime.date(2026, 3, 4))

    def test_slash(self):
        self.assertEqual(parse_jp_date("2026/03/04"), datetime.date(2026, 3, 4))

    def test_iso(self):
        self.assertEqual(parse_jp_date("2026-03-04"), datetime.date(2026, 3, 4))

    def test_bad(self):
        with self.assertRaises(ValueError):
            parse_jp_date("3月4日")
