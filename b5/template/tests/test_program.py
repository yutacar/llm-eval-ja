import unittest
from minical import evaluate, EvalError


class TestProgram(unittest.TestCase):
    def test_assignment(self):
        self.assertEqual(evaluate("x = 3; y = x * 2; y + 1"), 7)

    def test_newlines(self):
        self.assertEqual(evaluate("a = 2\nb = a ^ 3\nb - 1"), 7)

    def test_names_with_digits(self):
        self.assertEqual(evaluate("x1 = 4; x2 = 5; x1 * x2"), 20)

    def test_undefined(self):
        with self.assertRaises(EvalError):
            evaluate("y + 1")

    def test_functions(self):
        self.assertEqual(evaluate("abs(-3)"), 3)
        self.assertEqual(evaluate("max(1, 5, 3)"), 5)
        self.assertEqual(evaluate("min(4, 2)"), 2)

    def test_unknown_function(self):
        with self.assertRaises(EvalError):
            evaluate("foo(1)")

    def test_empty(self):
        self.assertIsNone(evaluate(""))
