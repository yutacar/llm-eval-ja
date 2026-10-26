import datetime
import unittest
from minishop.money import round_yen
from minishop.cart import Cart
from minishop.discount import apply_coupon
from minishop.paginate import paginate
from minishop.dates import parse_jp_date


class TestHidden(unittest.TestCase):
    def test_round_more(self):
        self.assertEqual(round_yen(0.5), 1)
        self.assertEqual(round_yen(1.5), 2)
        self.assertEqual(round_yen(1234.5), 1235)
        self.assertEqual(round_yen(10.49), 10)

    def test_three_carts(self):
        a, b, c = Cart(), Cart(), Cart()
        a.add("x", 100)
        b.add("y", 200, 2)
        self.assertEqual((a.count(), b.count(), c.count()), (1, 2, 0))

    def test_coupon_more(self):
        self.assertEqual(apply_coupon(2999, "YEN500"), 2999)
        self.assertEqual(apply_coupon(3001, "YEN500"), 2501)
        self.assertEqual(apply_coupon(300, "PCT10"), 270)

    def test_paginate_more(self):
        items = list(range(1, 24))
        self.assertEqual(paginate(items, 2, 10), list(range(11, 21)))
        self.assertEqual(paginate(items, 4, 10), [])
        self.assertEqual(paginate(items, 5, 5), [21, 22, 23])

    def test_dates_more(self):
        self.assertEqual(parse_jp_date("2026/12/31"), datetime.date(2026, 12, 31))
        self.assertEqual(parse_jp_date("2026/1/9"), datetime.date(2026, 1, 9))
