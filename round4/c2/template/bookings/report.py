"""集計。"""
import collections
import datetime
import time
import warnings

from . import store, timeutil


def daily_summary():
    """{日付(YYYY-MM-DD): 予約数}。"""
    c = collections.Counter(str(timeutil.to_local_date(b["start"])) for b in store.all_bookings())
    return dict(sorted(c.items()))


def weekend_bookings():
    """土日の予約の id。"""
    return [b["id"] for b in store.all_bookings() if time.localtime(b["start"]).tm_wday >= 5]


def monthly_minutes(year, month):
    """その月に始まる予約の合計分数。"""
    total = 0
    for b in store.all_bookings():
        d = datetime.date.fromtimestamp(b["start"])
        if (d.year, d.month) == (year, month):
            total += (b["end"] - b["start"]) // 60
    return total


def legacy_csv():
    warnings.warn("legacy_csv() is deprecated; use daily_summary()", DeprecationWarning, stacklevel=2)
    return "\n".join(f"{k},{v}" for k, v in daily_summary().items())
