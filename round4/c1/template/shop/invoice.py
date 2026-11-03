from .payments import charge


def bill_all(rows):
    """rows は {"user_id":..., "amount":..., "currency":...} の並び。currency は省略可。"""
    receipts = []
    for row in rows:
        kw = {"user_id": row["user_id"], "amount": row["amount"]}
        if "currency" in row:
            kw["currency"] = row["currency"]
        receipts.append(charge(**kw, note="invoice"))
    return receipts
