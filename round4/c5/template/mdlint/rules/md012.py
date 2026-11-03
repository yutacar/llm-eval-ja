"""MD012: 空行が2つ以上続く。"""
ID = "MD012"


def check(lines, cfg):
    blank = 0
    for i, l in enumerate(lines, 1):
        blank = blank + 1 if not l.strip() else 0
        if blank == 2:
            yield i, "multiple consecutive blank lines"
