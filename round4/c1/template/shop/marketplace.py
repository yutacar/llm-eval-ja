from .payments import charge

FEE_RATE = 0.1


def buy_from_seller(buyer_id, seller_id, price):
    """買い手に price を請求し、手数料（1割、切り捨て）を売り手に請求する。"""
    fee = int(price * FEE_RATE)
    jobs = [(buyer_id, price, "purchase"), (seller_id, fee, "market fee")]
    return [charge(uid, amt, note=what) for uid, amt, what in jobs if amt > 0]
