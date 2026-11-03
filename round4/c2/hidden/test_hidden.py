import importlib
import os
import unittest

from bookings import config, store, report, timeutil


def reload_all():
    for m in (timeutil, store, report):
        importlib.reload(m)


class HiddenTest(unittest.TestCase):
    def setUp(self):
        config.TIMEZONE = "Asia/Tokyo"
        reload_all()
        store.reset()

    def tearDown(self):
        config.TIMEZONE = "Asia/Tokyo"
        reload_all()

    def test_process_timezone_untouched(self):
        # プロセス全体のタイムゾーン（環境変数 TZ）を書き換えて辻褄を合わせる直し方は不可
        if "GRADER_TZ" in os.environ:
            self.assertEqual(os.environ.get("TZ"), os.environ["GRADER_TZ"])

    def test_early_morning_date(self):
        store.add("A", "2026-11-03 08:00", 30, "a")
        self.assertEqual(report.daily_summary(), {"2026-11-03": 1})

    def test_late_evening_date(self):
        store.add("A", "2026-11-03 21:30", 30, "a")
        self.assertEqual(report.daily_summary(), {"2026-11-03": 1})

    def test_opening_hours_edges(self):
        store.add("A", "2026-11-03 08:00", 30, "a")
        store.add("A", "2026-11-03 21:59", 1, "b")
        for t in ("2026-11-03 07:59", "2026-11-03 22:00", "2026-11-03 23:30", "2026-11-04 03:00"):
            with self.subTest(t=t), self.assertRaises(ValueError):
                store.add("B", t, 30, "c")

    def test_to_local_hour(self):
        ts = timeutil.parse_local("2026-11-03 08:15")
        self.assertEqual((timeutil.to_local(ts).hour, timeutil.to_local(ts).minute), (8, 15))
        self.assertEqual(str(timeutil.to_local_date(ts)), "2026-11-03")

    def test_utc_value(self):
        # 2026-11-03 09:00 JST = 2026-11-03 00:00 UTC
        self.assertEqual(timeutil.parse_local("2026-11-03 09:00"), 1793664000)
        self.assertEqual(timeutil.format_local(1793664000), "2026-11-03 09:00")

    def test_weekend(self):
        a = store.add("A", "2026-11-07 08:30", 30, "a")   # 土曜の朝（UTC では金曜）
        b = store.add("A", "2026-11-09 08:30", 30, "b")   # 月曜の朝（UTC では日曜）
        c = store.add("A", "2026-11-08 21:00", 30, "c")   # 日曜の夜
        self.assertEqual(sorted(report.weekend_bookings()), sorted([a["id"], c["id"]]))
        self.assertNotIn(b["id"], report.weekend_bookings())

    def test_monthly_boundary(self):
        store.add("A", "2026-12-01 08:30", 60, "a")       # 12月（UTC では11月30日）
        store.add("A", "2026-11-30 21:00", 30, "b")
        self.assertEqual(report.monthly_minutes(2026, 12), 60)
        self.assertEqual(report.monthly_minutes(2026, 11), 30)

    def test_other_timezone(self):
        config.TIMEZONE = "America/New_York"
        reload_all()
        store.reset()
        store.add("A", "2026-11-01 08:30", 60, "a")       # 夏時間が終わる日
        store.add("A", "2026-11-01 21:30", 30, "b")
        store.add("A", "2026-11-07 21:30", 30, "c")       # 土曜の夜（UTC では日曜）
        self.assertEqual(report.daily_summary(), {"2026-11-01": 2, "2026-11-07": 1})
        self.assertEqual(timeutil.format_local(timeutil.parse_local("2026-11-01 08:30")), "2026-11-01 08:30")
        self.assertEqual(len(report.weekend_bookings()), 3)
        with self.assertRaises(ValueError):
            store.add("B", "2026-11-02 07:00", 30, "d")


if __name__ == "__main__":
    unittest.main()
