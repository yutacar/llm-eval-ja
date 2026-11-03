"""時刻の変換。予約は UNIX 時刻（秒）で保存している。"""
import datetime
from zoneinfo import ZoneInfo

from . import config


def zone():
    return ZoneInfo(config.TIMEZONE)


def to_local(ts):
    """UNIX 時刻を現地の日時にする。"""
    return datetime.datetime.fromtimestamp(ts)


def to_local_date(ts):
    return to_local(ts).date()


def parse_local(text):
    """"2026-11-03 08:30" のような config.TIMEZONE の日時を UNIX 時刻にする。"""
    t = datetime.datetime.strptime(text, "%Y-%m-%d %H:%M").replace(tzinfo=zone())
    return int(t.timestamp())


def format_local(ts):
    return to_local(ts).strftime("%Y-%m-%d %H:%M")
