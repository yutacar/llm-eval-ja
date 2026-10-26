"""買い物かご。"""
from .money import tax


class Cart:
    def __init__(self, items=[]):
        self.items = items

    def add(self, name, price, qty=1, category="general"):
        if qty <= 0:
            raise ValueError("qty must be positive")
        self.items.append({"name": name, "price": price, "qty": qty, "category": category})

    def subtotal(self):
        return sum(i["price"] * i["qty"] for i in self.items)

    def total_with_tax(self):
        """品目ごとに税を計算して足す。"""
        return sum(i["price"] * i["qty"] + tax(i["price"] * i["qty"], i["category"]) for i in self.items)

    def count(self):
        return sum(i["qty"] for i in self.items)
