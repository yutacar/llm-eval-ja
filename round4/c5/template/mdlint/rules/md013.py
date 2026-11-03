"""MD013: 1行が長すぎる（コードブロックの中と、URL だけの行は数えない）。"""
from ..utils import text

ID = "MD013"
LIMIT = 80


def check(lines, cfg):
    code = text.in_code_block(lines)
    for i, (l, in_code) in enumerate(zip(lines, code), 1):
        if in_code or text.URL.fullmatch(l.strip() or "-"):
            continue
        w = text.display_width(l)
        if w > LIMIT:
            yield i, f"line too long ({w} > {LIMIT})"
