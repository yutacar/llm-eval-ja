"""MD001: 見出しのレベルは1つずつ上げる。"""
ID = "MD001"


def check(lines, cfg):
    prev = 0
    for i, l in enumerate(lines, 1):
        if l.startswith("#"):
            lv = len(l) - len(l.lstrip("#"))
            if prev and lv > prev + 1:
                yield i, f"heading level jumps from {prev} to {lv}"
            prev = lv
