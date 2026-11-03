"""MD027: 引用の > の後の空白が多すぎる。"""
ID = "MD027"


def check(lines, cfg):
    for i, l in enumerate(lines, 1):
        if l.startswith(">  "):
            yield i, "multiple spaces after blockquote symbol"
