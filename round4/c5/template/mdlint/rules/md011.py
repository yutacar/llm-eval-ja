"""MD011: リンクの書き方が逆 (text)[url]。"""
ID = "MD011"


def check(lines, cfg):
    import re
    for i, l in enumerate(lines, 1):
        if re.search(r"\([^)]+\)\[[^\]]+\]", l):
            yield i, "reversed link syntax"
