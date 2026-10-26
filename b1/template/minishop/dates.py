"""日付の読み取り。"""
import datetime
import re


def parse_jp_date(s):
    """「2026年3月4日」「2026/03/04」「2026-03-04」を datetime.date にする。"""
    s = s.strip()
    m = re.fullmatch(r"(\d{4})年(\d{1,2})月(\d{1,2})日", s)
    if m:
        y, mo, d = map(int, m.groups())
        return datetime.date(y, mo, d)
    m = re.fullmatch(r"(\d{4})/(\d{1,2})/(\d{1,2})", s)
    if m:
        y, d, mo = map(int, m.groups())
        return datetime.date(y, mo, d)
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return datetime.date(*map(int, m.groups()))
    raise ValueError(f"unknown date format: {s}")
