import unittest
from minical import evaluate, EvalError


class TestHidden(unittest.TestCase):
    def test_power_more(self):
        self.assertEqual(evaluate("-2 ^ -2"), -0.25)
        self.assertEqual(evaluate("2 ^ 3 ^ 0"), 2)
        self.assertEqual(evaluate("-3 ^ 2 ^ 2"), -81)

    def test_intdiv_more(self):
        self.assertEqual(evaluate("-8 // 3"), -2)
        self.assertEqual(evaluate("8 // -3"), -2)
        self.assertEqual(evaluate("-8 % 3"), -2)
        self.assertEqual(evaluate("-7.5 // 2"), -3.0)

    def test_numbers_more(self):
        self.assertEqual(evaluate("3E2"), 300.0)
        self.assertEqual(evaluate(".25 * 4"), 1.0)

    def test_names_more(self):
        self.assertEqual(evaluate("_a9 = 1; total_2 = _a9 + 1; total_2"), 2)

    def test_nested_calls(self):
        self.assertEqual(evaluate("max(min(3, 9), 2, abs(-7))"), 7)
        self.assertEqual(evaluate("min(5, 4, 3, 2, 1)"), 1)

    def test_unary_more(self):
        self.assertEqual(evaluate("- - 3"), 3)
        self.assertEqual(evaluate("+-3"), -3)
