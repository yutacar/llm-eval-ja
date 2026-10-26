import datetime
import unittest
from minishop.csvio import read_orders

CSV = """date,name,price,qty,category
2026年3月4日,"りんご, 青森産",150,3,food
2026-03-05,ノート,200,1,
"""


class TestCsv(unittest.TestCase):
    def test_read(self):
        rows = read_orders(CSV)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["name"], "りんご, 青森産")
        self.assertEqual(rows[0]["date"], datetime.date(2026, 3, 4))
        self.assertEqual(rows[1]["category"], "general")
