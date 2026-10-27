import unittest
from minical import evaluate, EvalError


class TestOperators(unittest.TestCase):
    def test_precedence(self):
        self.assertEqual(evaluate("1 + 2 * 3"), 7)
        self.assertEqual(evaluate("(1 + 2) * 3"), 9)

    def test_power_right_assoc(self):
        self.assertEqual(evaluate("2 ^ 3 ^ 2"), 512)

    def test_unary_minus_and_power(self):
        self.assertEqual(evaluate("-2 ^ 2"), -4)
        self.assertEqual(evaluate("(-2) ^ 2"), 4)
        self.assertEqual(evaluate("2 ^ -1"), 0.5)

    def test_true_division(self):
        self.assertEqual(evaluate("7 / 2"), 3.5)

    def test_int_division_truncates(self):
        self.assertEqual(evaluate("7 // 2"), 3)
        self.assertEqual(evaluate("-7 // 2"), -3)

    def test_modulo_sign(self):
        self.assertEqual(evaluate("7 % 3"), 1)
        self.assertEqual(evaluate("-7 % 2"), -1)

    def test_division_by_zero(self):
        for src in ("1 / 0", "1 // 0", "1 % 0"):
            with self.assertRaises(EvalError):
                evaluate(src)
