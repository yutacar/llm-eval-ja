"""MD022: 見出しの前後に空行。"""
ID = "MD022"


def check(lines, cfg):
    for i, l in enumerate(lines, 1):
        if l.startswith("#") and i < len(lines) and lines[i].strip():
            yield i, "heading should be followed by a blank line"
