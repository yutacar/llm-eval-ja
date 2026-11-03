"""MD036: 強調を見出しの代わりに使っている。"""
ID = "MD036"


def check(lines, cfg):
    import re
    for i, l in enumerate(lines, 1):
        if re.fullmatch(r"\*\*[^*]+\*\*", l.strip()):
            yield i, "emphasis used instead of a heading"
