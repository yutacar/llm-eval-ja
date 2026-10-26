"""クーポン。"""
from .money import round_yen


def apply_coupon(amount, coupon):
    """クーポン適用後の金額を返す。0 円より下にはしない。未知のクーポンは ValueError。

    PCT10 : 10% 引き（端数は四捨五入）
    YEN500: 3,000 円以上の注文で 500 円引き
    """
    if coupon is None:
        return amount
    if coupon == "PCT10":
        return round_yen(amount * 0.9)
    if coupon == "YEN500":
        if amount > 3000:
            return max(0, amount - 500)
        return amount
    raise ValueError(f"unknown coupon: {coupon}")
