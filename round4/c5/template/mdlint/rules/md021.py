"""MD021: 閉じる # の空白が多すぎる。"""
ID = "MD021"


def check(lines, cfg):
    for i, l in enumerate(lines, 1):
        if l.startswith("#") and l.rstrip().endswith("#") and l.rstrip().rstrip("#").endswith("  "):
            yield i, "multiple spaces before closing hashes"
