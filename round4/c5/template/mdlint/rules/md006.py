"""MD006: 行頭のリスト記号の前に空白。"""
ID = "MD006"


def check(lines, cfg):
    for i, l in enumerate(lines, 1):
        if l.startswith(" ") and l.lstrip()[:2] in ("- ", "* ") and (i == 1 or not lines[i - 2].strip()):
            yield i, "list should start at the beginning of the line"
