"""MD028: 引用の中の空行。"""
ID = "MD028"


def check(lines, cfg):
    for i, l in enumerate(lines, 1):
        if 1 < i < len(lines) and not l.strip() and lines[i - 2].startswith(">") and lines[i].startswith(">"):
            yield i, "blank line inside blockquote"
