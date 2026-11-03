"""MD026: 見出しの末尾に句読点。"""
ID = "MD026"


def check(lines, cfg):
    for i, l in enumerate(lines, 1):
        if l.startswith("#") and l.rstrip().endswith((".", "。", ":", "：", "!", "！")):
            yield i, "trailing punctuation in heading"
