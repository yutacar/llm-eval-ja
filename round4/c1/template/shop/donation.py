from .payments import charge

ROUND_TO = 100


def round_up_donation(user_id, price):
    """端数を100円単位に切り上げ、差額を寄付として請求する。差額が0なら None。"""
    diff = -price % ROUND_TO
    return charge(user_id, diff, "JPY", "donation") if diff else None
