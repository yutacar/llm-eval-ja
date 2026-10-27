#!/usr/bin/env python3
"""B4（新しいツールを作る：家計簿 CSV 集計）の採点。用意した入力で kakeibo.py を動かし、出力を照らし合わせる。

例:  python3 grade_b4.py ~/work/b4-ud-iq4_xs
"""
import pathlib, subprocess, sys, tempfile

CSV_MAIN = """date,category,amount,memo
2026-09-28,食費,1200,スーパー
2026-09-30,交通,"2,400",定期券の残り
2026-10-01,食費,800,
2026-10-02,日用品,abc,不正な金額
2026-10-03,食費,"1,500","弁当, お茶"
2026-10-05,交通,-400,払い戻し
2026-02-30,食費,999,存在しない日付
2026-10-07,趣味,3000,本
2026-10-07,日用品,3000,洗剤
,食費,100,日付なし
2026-11-01,食費,700,
2026-10-09,,500,カテゴリなし
2026-10-10,交通,1300,バス
"""
# 有効な行（行番号）: 2,3,4,6,7,9,10,12,14  不正: 5,8,11,13
EXPECT = {
    ("summary",): "食費\t4200\n交通\t3300\n日用品\t3000\n趣味\t3000\n合計\t13500\n",
    ("summary", "--month", "2026-10"): "日用品\t3000\n趣味\t3000\n食費\t2300\n交通\t900\n合計\t9200\n",
    ("summary", "--month", "2025-01"): "合計\t0\n",
    ("monthly",): "2026-09\t3600\n2026-10\t9200\n2026-11\t700\n",
    ("top", "3"): "2026-10-07\t趣味\t3000\t本\n2026-10-07\t日用品\t3000\t洗剤\n2026-09-30\t交通\t2400\t定期券の残り\n",
    ("top", "100"): ("2026-10-07\t趣味\t3000\t本\n2026-10-07\t日用品\t3000\t洗剤\n2026-09-30\t交通\t2400\t定期券の残り\n"
                     "2026-10-03\t食費\t1500\t弁当, お茶\n2026-10-10\t交通\t1300\tバス\n2026-09-28\t食費\t1200\tスーパー\n"
                     "2026-10-01\t食費\t800\t\n2026-11-01\t食費\t700\t\n2026-10-05\t交通\t-400\t払い戻し\n"),
}


def run(d, args, csv_text=None, name="data.csv", bom=False):
    with tempfile.TemporaryDirectory() as t:
        t = pathlib.Path(t)
        if csv_text is not None:
            (t / name).write_bytes(("﻿" if bom else "").encode() + csv_text.encode("utf-8"))
        cmd = [sys.executable, str(d / "kakeibo.py"), args[0], str(t / name)] + list(args[1:])
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=t)
        return p.returncode, p.stdout, p.stderr


def norm(s):
    return "\n".join(l.rstrip("\r") for l in s.strip("\n").split("\n")) + "\n" if s.strip() else ""


def main():
    if len(sys.argv) != 2:
        print("使い方: python3 grade_b4.py <作業フォルダ>")
        sys.exit(1)
    d = pathlib.Path(sys.argv[1]).expanduser()
    if not (d / "kakeibo.py").exists():
        print("kakeibo.py がありません")
        sys.exit(1)
    results = []

    def check(name, ok, detail=""):
        results.append(ok)
        print(f"{'○' if ok else '×'} {name}" + (f"\n    {detail}" if (detail and not ok) else ""))

    for args, want in EXPECT.items():
        rc, out, err = run(d, args, CSV_MAIN)
        check(" ".join(args), rc == 0 and norm(out) == norm(want), f"終了コード {rc} / 出力: {out[:200]!r}")
    rc, out, err = run(d, ("summary",), CSV_MAIN)
    lines = [l for l in err.splitlines() if l.startswith("skip line")]
    nums = sorted(int(l.split()[2].rstrip(":")) for l in lines if l.split()[2].rstrip(":").isdigit())
    check("不正な行の報告（skip line 5, 8, 11, 13）", nums == [5, 8, 11, 13], f"標準エラー: {err[:200]!r}")
    rc, out, err = run(d, ("summary",), CSV_MAIN, bom=True)
    check("BOM 付きの CSV", rc == 0 and norm(out) == norm(EXPECT[("summary",)]), f"出力: {out[:120]!r}")
    rc, out, err = run(d, ("summary",), None, name="nothing.csv")
    check("ファイルが無いとき（終了コード 1）", rc == 1 and "error: file not found:" in err, f"終了コード {rc} / {err[:120]!r}")
    rc, out, err = run(d, ("top", "0"), CSV_MAIN)
    check("top 0（終了コード 2）", rc == 2, f"終了コード {rc}")
    rc, out, err = run(d, ("top", "x"), CSV_MAIN)
    check("top x（終了コード 2）", rc == 2, f"終了コード {rc}")
    rc, out, err = run(d, ("hello",), CSV_MAIN)
    check("不正なコマンド（終了コード 2）", rc == 2, f"終了コード {rc}")
    own = subprocess.run([sys.executable, "-m", "unittest"], cwd=d, capture_output=True, text=True, timeout=120)
    ran = next((l for l in own.stderr.splitlines() if l.startswith("Ran ")), "Ran 0 tests")
    print(f"（参考）自作テスト: {ran} / {'OK' if own.returncode == 0 else 'FAILED'}")
    print(f"合計: {sum(results)}/{len(results)}")


if __name__ == "__main__":
    main()
