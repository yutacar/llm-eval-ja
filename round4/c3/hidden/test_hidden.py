import datetime
import unittest

from jpdata.normalize import normalize
from jpdata.wareki import to_seireki, to_wareki
from jpdata.address import split_address
from jpdata.zipcode import normalize_zip


class NormalizeTest(unittest.TestCase):
    def check(self, cases):
        for src, want in cases:
            with self.subTest(src=src):
                self.assertEqual(normalize(src), want)

    def test_fullwidth(self):
        self.check([("ＡＢＣ　１２３", "ABC 123"), ("Ｐｙｔｈｏｎ！？", "Python!?"), ("（株）", "(株)")])

    def test_halfwidth_kana(self):
        self.check([("ﾊﾟｿｺﾝ", "パソコン"), ("ｳﾞｧｲｵﾘﾝ", "ヴァイオリン"), ("ｺｰﾋｰ", "コーヒー"),
                    ("ｱｲｳ｡｢ﾃｽﾄ｣", "アイウ。「テスト」")])

    def test_no_extra_conversion(self):
        self.check([("①番", "①番"), ("㈱テスト", "㈱テスト"), ("ⅳ章", "ⅳ章")])

    def test_hyphens(self):
        self.check([("1‐2", "1-2"), ("3–4", "3-4"), ("5−6", "5-6"), ("7―8", "7-8"),
                    ("TEL 03－1234－5678", "TEL 03-1234-5678"), ("スーパー1ー2", "スーパー1-2"), ("ー1", "ー1")])

    def test_spaces(self):
        self.check([("  あ   い  ", "あ い"), ("　東京　　都　", "東京 都")])


class WarekiTest(unittest.TestCase):
    def test_to_seireki(self):
        for src, want in [("令和7年11月3日", "2025-11-03"), ("令和７年１１月３日", "2025-11-03"),
                          ("平成1年1月8日", "1989-01-08"), ("平成元年1月8日", "1989-01-08"),
                          ("平成31年4月30日", "2019-04-30"), ("昭和64年1月7日", "1989-01-07"),
                          ("昭和元年12月25日", "1926-12-25"), ("大正15年12月24日", "1926-12-24"),
                          ("大正元年7月30日", "1912-07-30"), ("明治45年7月29日", "1912-07-29"),
                          ("明治6年1月1日", "1873-01-01"), ("平成12年2月29日", "2000-02-29")]:
            with self.subTest(src=src):
                self.assertEqual(to_seireki(src), want)

    def test_to_seireki_invalid(self):
        for src in ["令和元年4月30日", "昭和64年1月8日", "大正15年12月25日", "明治45年7月30日", "平成13年2月29日",
                    "令和0年5月1日", "明治5年12月31日", "大化元年1月1日", "令和2年13月1日"]:
            with self.subTest(src=src), self.assertRaises(ValueError):
                to_seireki(src)

    def test_to_wareki(self):
        for src, want in [("2019-05-01", "令和元年5月1日"), ("2019-04-30", "平成31年4月30日"),
                          ("1989-01-08", "平成元年1月8日"), ("1926-12-25", "昭和元年12月25日"),
                          ("1926-12-24", "大正15年12月24日"), ("1912-07-30", "大正元年7月30日"),
                          ("1912-07-29", "明治45年7月29日"), ("1873-01-01", "明治6年1月1日"),
                          (datetime.date(2025, 11, 3), "令和7年11月3日")]:
            with self.subTest(src=src):
                self.assertEqual(to_wareki(src), want)

    def test_to_wareki_too_old(self):
        with self.assertRaises(ValueError):
            to_wareki("1872-12-31")


class AddressTest(unittest.TestCase):
    def test_split(self):
        for src, want in [
            ("東京都町田市森野2-2-22", ("東京都", "町田市", "森野2-2-22")),
            ("三重県四日市市諏訪町1-5", ("三重県", "四日市市", "諏訪町1-5")),
            ("広島県廿日市市下平良1-11-1", ("広島県", "廿日市市", "下平良1-11-1")),
            ("石川県野々市市三納1-1", ("石川県", "野々市市", "三納1-1")),
            ("千葉県市川市八幡1-1-1", ("千葉県", "市川市", "八幡1-1-1")),
            ("千葉県市原市国分寺台中央1-1-1", ("千葉県", "市原市", "国分寺台中央1-1-1")),
            ("新潟県十日町市千歳町3-3", ("新潟県", "十日町市", "千歳町3-3")),
            ("新潟県村上市三之町1-1", ("新潟県", "村上市", "三之町1-1")),
            ("山形県村山市中央1-3-6", ("山形県", "村山市", "中央1-3-6")),
            ("東京都東村山市本町1-2-3", ("東京都", "東村山市", "本町1-2-3")),
            ("東京都武蔵村山市本町1-1-1", ("東京都", "武蔵村山市", "本町1-1-1")),
            ("奈良県大和郡山市北郡山町248-4", ("奈良県", "大和郡山市", "北郡山町248-4")),
            ("福島県郡山市朝日1-23-7", ("福島県", "郡山市", "朝日1-23-7")),
            ("福岡県小郡市小郡255-1", ("福岡県", "小郡市", "小郡255-1")),
            ("長野県大町市大町3887", ("長野県", "大町市", "大町3887")),
            ("北海道虻田郡倶知安町北1条東3", ("北海道", "虻田郡倶知安町", "北1条東3")),
            ("神奈川県足柄下郡箱根町湯本256", ("神奈川県", "足柄下郡箱根町", "湯本256")),
            ("沖縄県島尻郡北大東村字中野", ("沖縄県", "島尻郡北大東村", "字中野")),
            ("大阪府大阪市北区中之島1-3-20", ("大阪府", "大阪市北区", "中之島1-3-20")),
            ("京都府京都市中京区寺町通御池上る上本能寺前町488", ("京都府", "京都市中京区", "寺町通御池上る上本能寺前町488")),
            ("京都市左京区吉田本町", ("", "京都市左京区", "吉田本町")),
            ("埼玉県さいたま市浦和区常盤6-4-4", ("埼玉県", "さいたま市浦和区", "常盤6-4-4")),
            ("宮城県仙台市青葉区国分町3-7-1", ("宮城県", "仙台市青葉区", "国分町3-7-1")),
            ("静岡県浜松市中央区元城町103-2", ("静岡県", "浜松市中央区", "元城町103-2")),
            ("群馬県前橋市大手町1-1-1", ("群馬県", "前橋市", "大手町1-1-1")),
            ("東京都千代田区丸の内１－１", ("東京都", "千代田区", "丸の内1-1")),
        ]:
            with self.subTest(src=src):
                self.assertEqual(tuple(split_address(src)), want)


class ZipTest(unittest.TestCase):
    def test_valid(self):
        for src in ["1000001", "100-0001", "〒100-0001", "１００－０００１", "100ー0001", " 100-0001 "]:
            with self.subTest(src=src):
                self.assertEqual(normalize_zip(src), "100-0001")

    def test_invalid(self):
        for src in ["100-00011", "10-00001", "1000-001", "abc-defg", "100 0001", "100-000a", "", "1000-0001"]:
            with self.subTest(src=src):
                self.assertIsNone(normalize_zip(src))


if __name__ == "__main__":
    unittest.main()
