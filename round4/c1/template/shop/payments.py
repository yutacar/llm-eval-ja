"""決済の入口。どの機能も最後はここの charge() を呼ぶ。"""
import itertools

from . import ledger

CURRENCIES = ("JPY", "USD", "EUR")
_ids = itertools.count(1)


def charge(user_id, amount, currency="JPY", note=None):
    """user_id に amount を請求し、領収書の辞書を返す。"""
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("user_id must be a positive int")
    if not isinstance(amount, int) or amount <= 0:
        raise ValueError("amount must be a positive int")
    if currency not in CURRENCIES:
        raise ValueError(f"unsupported currency: {currency}")
    receipt = {"id": next(_ids), "user_id": user_id, "amount": amount, "currency": currency, "note": note}
    ledger.record(receipt)
    return receipt
