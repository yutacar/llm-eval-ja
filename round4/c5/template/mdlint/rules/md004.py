"""MD004: リストの記号をそろえる。"""
ID = "MD004"


def check(lines, cfg):
    marks = set()
    for i, l in enumerate(lines, 1):
        s = l.lstrip()
        if s[:2] in ("- ", "* ", "+ "):
            marks.add(s[0])
            if len(marks) > 1:
                yield i, "mixed list markers"
                return
