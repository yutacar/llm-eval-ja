import unittest
from minical import evaluate


class TestNumbers(unittest.TestCase):
    def test_int_and_float(self):
        self.assertEqual(evaluate("12"), 12)
        self.assertIsInstance(evaluate("12"), int)
        self.assertEqual(evaluate("3.5"), 3.5)

    def test_leading_dot(self):
        self.assertEqual(evaluate(".5 + 1"), 1.5)

    def test_exponent(self):
        self.assertEqual(evaluate("1e3"), 1000.0)
        self.assertAlmostEqual(evaluate("2.5E-2"), 0.025)
