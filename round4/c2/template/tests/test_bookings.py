import unittest
import warnings

from bookings import store, report, timeutil


class BookingTest(unittest.TestCase):
    def setUp(self):
        store.reset()

    def test_daily_summary(self):
        store.add("A", "2026-11-03 08:30", 60, "sato")
        store.add("A", "2026-11-03 10:00", 30, "kato")
        store.add("B", "2026-11-03 21:00", 60, "ito")
        store.add("B", "2026-11-04 09:00", 60, "ito")
        self.assertEqual(report.daily_summary(), {"2026-11-03": 3, "2026-11-04": 1})

    def test_overlap(self):
        store.add("A", "2026-11-03 10:00", 60, "sato")
        with self.assertRaises(ValueError):
            store.add("A", "2026-11-03 10:30", 30, "kato")

    def test_opening_hours(self):
        with self.assertRaises(ValueError):
            store.add("A", "2026-11-03 07:30", 30, "sato")

    def test_format_roundtrip(self):
        self.assertEqual(timeutil.format_local(timeutil.parse_local("2026-11-03 08:30")), "2026-11-03 08:30")

    def test_legacy_csv(self):
        store.add("A", "2026-11-05 12:00", 30, "sato")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertEqual(report.legacy_csv(), "2026-11-05,1")


if __name__ == "__main__":
    unittest.main()
