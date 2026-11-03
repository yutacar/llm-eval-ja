from .payments import charge


class Cart:
    def __init__(self, user_id):
        self.user_id = user_id
        self.items = []          # (name, price, qty)

    def add(self, name, price, qty=1):
        self.items.append((name, price, qty))

    def total(self):
        return sum(p * q for _, p, q in self.items)

    def checkout(self):
        if not self.items:
            raise ValueError("cart is empty")
        receipt = charge(self.user_id, self.total(), note=f"cart:{len(self.items)} items")
        self.items = []
        return receipt
