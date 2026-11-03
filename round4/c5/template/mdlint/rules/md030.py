"""MD030: リスト記号の後の空白。"""
ID = "MD030"


def check(lines, cfg):
    for i, l in enumerate(lines, 1):
        s = l.lstrip()
        if s[:3] in ("-  ", "*  ", "+  "):
            yield i, "multiple spaces after list marker"
