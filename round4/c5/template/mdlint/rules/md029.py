"""MD029: 番号付きリストの番号。"""
ID = "MD029"


def check(lines, cfg):
    import re
    want = None
    for i, l in enumerate(lines, 1):
        m = re.match(r"(\d+)\. ", l)
        if not m:
            want = None
            continue
        n = int(m[1])
        if want is not None and n not in (want, 1):
            yield i, f"ordered list item should be {want}"
        want = n + 1
