"""MD019: # の後の空白が多すぎる。"""
ID = "MD019"


def check(lines, cfg):
    for i, l in enumerate(lines, 1):
        if l.startswith("#") and l.lstrip("#").startswith("  "):
            yield i, "multiple spaces after hash"
