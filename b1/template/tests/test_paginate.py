import unittest
from minishop.paginate import paginate, page_count


class TestPaginate(unittest.TestCase):
    def setUp(self):
        self.items = list(range(1, 24))   # 1..23

    def test_first_page(self):
        self.assertEqual(paginate(self.items, 1, 10), list(range(1, 11)))

    def test_last_page(self):
        self.assertEqual(paginate(self.items, 3, 10), [21, 22, 23])

    def test_page_count(self):
        self.assertEqual(page_count(23, 10), 3)
        self.assertEqual(page_count(0, 10), 1)

    def test_bad_page(self):
        with self.assertRaises(ValueError):
            paginate(self.items, 0, 10)
