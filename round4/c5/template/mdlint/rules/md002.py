"""MD002: 最初の見出しはレベル1。"""
ID = "MD002"


def check(lines, cfg):
    for i, l in enumerate(lines, 1):
        if l.startswith("#"):
            if not l.startswith("# "):
                yield i, "first heading should be level 1"
            return
