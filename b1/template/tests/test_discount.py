import unittest
from minishop.discount import apply_coupon


class TestDiscount(unittest.TestCase):
    def test_none(self):
        self.assertEqual(apply_coupon(1000, None), 1000)

    def test_pct10(self):
        self.assertEqual(apply_coupon(1000, "PCT10"), 900)

    def test_yen500(self):
        self.assertEqual(apply_coupon(5000, "YEN500"), 4500)
        self.assertEqual(apply_coupon(2000, "YEN500"), 2000)

    def test_yen500_boundary(self):
        self.assertEqual(apply_coupon(3000, "YEN500"), 2500)

    def test_unknown(self):
        with self.assertRaises(ValueError):
            apply_coupon(1000, "FREE")
