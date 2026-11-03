from . import payments

_balance = {}


def add_points(user_id, pts):
    _balance[user_id] = _balance.get(user_id, 0) + pts


def balance(user_id):
    return _balance.get(user_id, 0)


def reset():
    _balance.clear()


def pay_with_points(user_id, price):
    """ポイント（1pt=1円）を先に使い、足りない分だけ請求する。全部ポイントで払えたら None。"""
    used = min(balance(user_id), price)
    _balance[user_id] = balance(user_id) - used
    rest = price - used
    if rest == 0:
        return None
    pay = payments.charge
    return pay(user_id, rest, note=f"points used:{used}")
