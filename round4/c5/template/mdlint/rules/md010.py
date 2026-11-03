"""MD010: タブ文字。"""
ID = "MD010"


def check(lines, cfg):
    for i, l in enumerate(lines, 1):
        if "\t" in l:
            yield i, "hard tab"
