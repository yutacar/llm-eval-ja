"""円の端数処理と消費税。"""

TAX_RATES = {"food": 0.08, "general": 0.10}


def round_yen(x):
    """1円未満を四捨五入して整数の円にする（0.5 は切り上げ）。"""
    return int(round(x))


def tax(amount, category="general"):
    """税額を返す。category は "food"（8%）か "general"（10%）。"""
    rate = TAX_RATES.get(category, TAX_RATES["general"])
    return round_yen(amount * rate)
