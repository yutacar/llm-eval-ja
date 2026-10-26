import unittest
from minishop.money import round_yen, tax


class TestMoney(unittest.TestCase):
    def test_round_basic(self):
        self.assertEqual(round_yen(10.4), 10)
        self.assertEqual(round_yen(10.6), 11)

    def test_round_half_up(self):
        self.assertEqual(round_yen(2.5), 3)
        self.assertEqual(round_yen(102.5), 103)

    def test_tax_general(self):
        self.assertEqual(tax(1000), 100)

    def test_tax_food(self):
        self.assertEqual(tax(1000, "food"), 80)
        self.assertEqual(tax(1250, "food"), 100)
