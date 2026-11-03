from . import payments


def apply_coupon(price, rate):
    """rate は割引率（0.1 なら1割引き）。1円未満は切り捨て。"""
    return int(price * (1 - rate))


def pay_with_coupon(user_id, price, rate):
    return payments.charge(user_id, apply_coupon(price, rate), "JPY", "coupon")
