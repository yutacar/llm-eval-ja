"""MD018: # の後に空白がない。"""
ID = "MD018"


def check(lines, cfg):
    for i, l in enumerate(lines, 1):
        if l.startswith("#") and len(l.lstrip("#")) and not l.lstrip("#").startswith(" "):
            yield i, "no space after hash"
