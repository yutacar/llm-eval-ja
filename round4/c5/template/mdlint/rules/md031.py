"""MD031: コードブロックの前に空行。"""
ID = "MD031"


def check(lines, cfg):
    inside = False
    for i, l in enumerate(lines, 1):
        if l.startswith("```"):
            if not inside and i > 1 and lines[i - 2].strip():
                yield i, "fenced code block should be preceded by a blank line"
            inside = not inside
