"""MD034: むき出しの URL。"""
ID = "MD034"


def check(lines, cfg):
    import re
    for i, l in enumerate(lines, 1):
        if re.search(r"(?<![(<])https?://\S+", l) and "](" not in l:
            yield i, "bare URL; wrap it in <...>"
