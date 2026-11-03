"""予約の保存（メモリ上）。"""
import itertools

from . import timeutil, config

_ids = itertools.count(1)
_bookings = []


def reset():
    _bookings.clear()


def add(room, start_text, minutes, who):
    start = timeutil.parse_local(start_text)
    hour = timeutil.to_local(start).hour
    if not (config.OPEN_HOUR <= hour < config.CLOSE_HOUR):
        raise ValueError(f"outside opening hours: {start_text}")
    b = {"id": next(_ids), "room": room, "start": start, "end": start + minutes * 60, "who": who}
    for o in _bookings:
        if o["room"] == room and o["start"] < b["end"] and b["start"] < o["end"]:
            raise ValueError(f"overlaps booking #{o['id']}")
    _bookings.append(b)
    return b


def all_bookings():
    return list(_bookings)
