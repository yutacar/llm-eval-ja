"""MD009: 行末の空白。"""
ID = "MD009"


def check(lines, cfg):
    if cfg["allow_trailing_spaces"]:
        return
    for i, l in enumerate(lines, 1):
        if l != l.rstrip(" "):
            yield i, "trailing spaces"
