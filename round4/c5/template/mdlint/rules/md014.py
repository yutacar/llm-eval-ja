"""MD014: コマンド例の先頭の $。"""
ID = "MD014"


def check(lines, cfg):
    for i, l in enumerate(lines, 1):
        if l.startswith("$ "):
            yield i, "dollar sign used before command"
