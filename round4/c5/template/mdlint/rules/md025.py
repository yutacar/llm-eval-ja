"""MD025: レベル1の見出しは1つだけ。"""
ID = "MD025"


def check(lines, cfg):
    n = 0
    for i, l in enumerate(lines, 1):
        if l.startswith("# "):
            n += 1
            if n == 2:
                yield i, "multiple top-level headings"
