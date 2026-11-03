"""MD007: リストの字下げの幅（indent_size）。"""
ID = "MD007"


def check(lines, cfg):
    for i, l in enumerate(lines, 1):
        s = l.lstrip(" ")
        n = len(l) - len(s)
        if s[:2] in ("- ", "* ", "+ ") and n % cfg["indent_size"]:
            yield i, f"list indent {n} is not a multiple of {cfg['indent_size']}"
