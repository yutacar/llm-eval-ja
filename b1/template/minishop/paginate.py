"""一覧のページ分け。"""
import math


def page_count(n_items, per_page):
    if per_page <= 0:
        raise ValueError("per_page must be positive")
    return max(1, math.ceil(n_items / per_page))


def paginate(items, page, per_page):
    """page 番目（1 から数える）のページの要素を返す。範囲外は空リスト。"""
    if page < 1:
        raise ValueError("page starts at 1")
    start = page * per_page
    return items[start:start + per_page]
