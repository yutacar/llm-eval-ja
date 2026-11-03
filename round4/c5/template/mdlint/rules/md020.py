"""MD020: 閉じる # の空白。"""
ID = "MD020"


def check(lines, cfg):
    for i, l in enumerate(lines, 1):
        if l.startswith("#") and l.rstrip().endswith("#") and not l.rstrip().rstrip("#").endswith(" "):
            yield i, "no space before closing hashes"
