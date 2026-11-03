"""MD024: 同じ見出しが重複。"""
ID = "MD024"


def check(lines, cfg):
    seen = set()
    for i, l in enumerate(lines, 1):
        if l.startswith("#"):
            if l in seen:
                yield i, "duplicate heading"
            seen.add(l)
