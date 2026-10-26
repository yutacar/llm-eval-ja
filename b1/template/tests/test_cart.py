import unittest
from minishop.cart import Cart


class TestCart(unittest.TestCase):
    def test_add_and_subtotal(self):
        c = Cart()
        c.add("りんご", 150, 3, "food")
        c.add("ノート", 200)
        self.assertEqual(c.subtotal(), 650)
        self.assertEqual(c.count(), 4)

    def test_total_with_tax(self):
        c = Cart()
        c.add("りんご", 150, 3, "food")   # 450 + 36
        c.add("ノート", 200)              # 200 + 20
        self.assertEqual(c.total_with_tax(), 706)

    def test_carts_are_independent(self):
        a = Cart()
        a.add("みかん", 100)
        b = Cart()
        self.assertEqual(b.count(), 0)

    def test_bad_qty(self):
        with self.assertRaises(ValueError):
            Cart().add("x", 100, 0)
