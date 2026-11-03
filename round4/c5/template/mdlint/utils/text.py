import re
import unicodedata


def split_lines(src):
    return src.split("\n")


def in_code_block(lines):
    """各行がコードブロック（``` の間）の中かどうか。"""
    inside, out = False, []
    for line in lines:
        if line.lstrip().startswith("```"):
            out.append(True)
            inside = not inside
        else:
            out.append(inside)
    return out


def display_width(s):
    """表示幅（全角は2）。"""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


URL = re.compile(r"https?://\S+")
