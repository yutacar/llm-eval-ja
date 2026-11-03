import datetime
import unittest

from jpdata.normalize import normalize
from jpdata.wareki import to_seireki, to_wareki
from jpdata.address import split_address
from jpdata.zipcode import normalize_zip


class JpdataTest(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize("ＡＢＣ１２３"), "ABC123")
        self.assertEqual(normalize("ｶﾞｲﾄﾞ"), "ガイド")
        self.assertEqual(normalize("03ー1234ー5678"), "03-1234-5678")

    def test_to_seireki(self):
        self.assertEqual(to_seireki("令和元年5月1日"), "2019-05-01")
        with self.assertRaises(ValueError):
            to_seireki("平成31年5月1日")

    def test_to_wareki(self):
        self.assertEqual(to_wareki(datetime.date(2019, 5, 1)), "令和元年5月1日")
        self.assertEqual(to_wareki("1989-01-07"), "昭和64年1月7日")

    def test_split_address(self):
        self.assertEqual(split_address("東京都千代田区丸の内1-1"), ("東京都", "千代田区", "丸の内1-1"))
        self.assertEqual(split_address("神奈川県横浜市中区日本大通1"), ("神奈川県", "横浜市中区", "日本大通1"))

    def test_zip(self):
        self.assertEqual(normalize_zip("〒1000001"), "100-0001")
        self.assertIsNone(normalize_zip("100-001"))


if __name__ == "__main__":
    unittest.main()
