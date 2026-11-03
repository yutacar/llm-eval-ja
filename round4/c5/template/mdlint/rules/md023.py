"""MD023: 見出しは行の先頭から。"""
ID = "MD023"


def check(lines, cfg):
    for i, l in enumerate(lines, 1):
        if l.startswith(" ") and l.lstrip().startswith("#"):
            yield i, "heading must start at the beginning of the line"
