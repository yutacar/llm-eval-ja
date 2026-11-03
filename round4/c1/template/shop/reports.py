"""集計（charge は呼ばない）。"""
from . import ledger


def total_by_currency():
    out = {}
    for e in ledger.entries():
        out[e["currency"]] = out.get(e["currency"], 0) + e["amount"]
    return out


def notes():
    # 例: charge(user_id, amount, ...) で付けたメモの一覧
    return [e["note"] for e in ledger.entries()]
