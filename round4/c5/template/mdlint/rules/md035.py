"""MD035: 水平線の書き方をそろえる。"""
ID = "MD035"


def check(lines, cfg):
    styles = set()
    for i, l in enumerate(lines, 1):
        if l.strip() in ("---", "***", "___"):
            styles.add(l.strip())
            if len(styles) > 1:
                yield i, "inconsistent horizontal rule style"
