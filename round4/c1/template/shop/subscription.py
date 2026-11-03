import functools

from .payments import charge

PLANS = {"basic": 980, "pro": 2980}


def renewer(user_id):
    """その人の更新用の関数を返す（毎月これを呼ぶ）。"""
    return functools.partial(charge, user_id, note="subscription")


def renew(user_id, plan):
    pay = renewer(user_id)
    return pay(PLANS[plan])
