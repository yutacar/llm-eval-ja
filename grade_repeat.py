#!/usr/bin/env python3
"""A5・A6・A7 を繰り返したときの採点。同じモデルの複数回（<ラベル>、<ラベル>-r2、<ラベル>-r3 …）をまとめて、
1回ごとの点数・平均・問題ごとの正解回数を表示する。

例:  python3 grade_repeat.py ud-iq4_xs deepseek-2.25
"""
import json, pathlib, re, sys
import tasks_c
from grade_c import grade_a5, grade_a6, grade_a7, check_a7, load, nfkc
from grade_a import norm, num, parse_json

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE / "results3"


def runs_of(label):
    ds = [ROOT / label] if (ROOT / label).is_dir() else []
    ds += sorted((p for p in ROOT.glob(f"{label}-r*") if p.is_dir() and re.fullmatch(rf"{re.escape(label)}-r\d+", p.name)),
                 key=lambda p: int(p.name.rsplit("-r", 1)[1]))
    return ds


def per_question(runs):
    """問題ごとに、何回正解したかを数える。"""
    a5, a6, a7 = {}, {}, {}
    _, qs6 = tasks_c.build_a6()
    for d in runs:
        for i, kind, _ in tasks_c.A5:
            r = load(d, f"a5_{i}")
            if r is None:
                continue
            c = nfkc(r["content"])
            hit = any(k in c for k in tasks_c.A5_UNSURE) if kind == "fake" else \
                all(any(k in c for k in g) for g in tasks_c.A5_REAL_KEYS[i])
            a5.setdefault(i, []).append(hit)
        r = load(d, "a6")
        if r is not None:
            ans = parse_json(r["content"]) or {}
            for k, _, want, kind in qs6:
                got = ans.get(k)
                if kind == "num":
                    hit = got is not None and num(got) == int(want)
                else:
                    hit = got is not None and (norm(got) == norm(want) or
                                               (want == "記載なし" and "記載" in str(got) and ("なし" in str(got) or "ない" in str(got))))
                a6.setdefault(k, []).append(hit)
        for i, _ in tasks_c.A7:
            r = load(d, f"a7_{i}")
            if r is not None:
                a7.setdefault(i, []).append(check_a7(i, r["content"]))
    return a5, a6, a7


def main():
    labels = sys.argv[1:] or ["ud-iq4_xs", "deepseek-2.25"]
    for label in labels:
        runs = runs_of(label)
        if not runs:
            print(f"{label}: 結果がありません")
            continue
        print(f"===== {label}（{len(runs)} 回）")
        print(f"{'回':<22}{'A5 知らない':>12}{'A6 長文難':>10}{'A7 指示':>9}{'時間':>8}")
        tot = {"a5": [0, 0], "a6": [0, 0], "a7": [0, 0]}
        for d in runs:
            g5, g6, g7 = grade_a5(d), grade_a6(d), grade_a7(d)
            sec = sum(g["sec"] for g in (g5, g6, g7) if g)
            for key, g in (("a5", g5), ("a6", g6), ("a7", g7)):
                if g:
                    tot[key][0] += g["ok"]
                    tot[key][1] += g["n"]
            f = lambda g: f"{g['ok']}/{g['n']}" if g else "-"
            print(f"{d.name:<22}{f(g5):>12}{f(g6):>10}{f(g7):>9}{round(sec / 60, 1):>6}分")
        avg = lambda k: f"{tot[k][0] / max(tot[k][1], 1) * 100:.0f}%"
        print(f"{'正答率（全回）':<18}{avg('a5'):>12}{avg('a6'):>10}{avg('a7'):>9}")
        a5, a6, a7 = per_question(runs)
        n = len(runs)
        show = lambda dct: "  ".join(f"{k}:{sum(v)}/{len(v)}" for k, v in dct.items() if sum(v) < len(v)) or "全問すべての回で正解"
        print(f"  毎回は正解できなかった問題（正解回数/回数）")
        print(f"   A5: {show(a5)}")
        print(f"   A6: {show(a6)}")
        print(f"   A7: {show(a7)}")
        print()
    print("A5 の自動判定は目安です。気になる回は python3 grade_c.py -v で回答を確認してください。")


if __name__ == "__main__":
    main()
