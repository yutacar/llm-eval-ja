"""MD005: 同じ階層のリストの字下げをそろえる。"""
ID = "MD005"


def check(lines, cfg):
    seen = {}
    for i, l in enumerate(lines, 1):
        s = l.lstrip()
        if s[:2] in ("- ", "* ", "+ ") and l != s and (len(l) - len(s)) % 2:
            yield i, "odd list indentation"
