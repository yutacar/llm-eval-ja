"""MD003: 見出しの書き方をそろえる（heading_style）。"""
ID = "MD003"


def check(lines, cfg):
    for i, l in enumerate(lines, 1):
        if cfg["heading_style"] == "atx" and i > 1 and l and set(l) <= {"="} and lines[i - 2].strip():
            yield i, "setext heading; use atx (# ...)"
