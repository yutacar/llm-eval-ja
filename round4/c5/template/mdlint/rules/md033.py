"""MD033: HTML のタグ。"""
ID = "MD033"


def check(lines, cfg):
    import re
    for i, l in enumerate(lines, 1):
        if re.search(r"<(div|span|font|center)\b", l):
            yield i, "inline HTML"
