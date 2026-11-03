"""MD032: リストの前後に空行。"""
ID = "MD032"


def check(lines, cfg):
    for i, l in enumerate(lines, 1):
        s = l.lstrip()
        if s[:2] in ("- ", "* ", "+ ") and i > 1 and lines[i - 2].strip() and not lines[i - 2].lstrip()[:2] in ("- ", "* ", "+ ") and not lines[i - 2].startswith(" "):
            yield i, "list should be surrounded by blank lines"
