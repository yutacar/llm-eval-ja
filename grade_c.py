#!/usr/bin/env python3
"""第3回（A3・A5・A6・A7・A8）の採点。results3/ の全ラベルを並べて表示する。

例:  python3 grade_c.py        # 表だけ
     python3 grade_c.py -v     # 間違い・回答の抜粋も表示（A5 は目で確認する）
"""
import json, pathlib, re, sys, unicodedata
import tasks_c
from grade_a import norm, num, parse_json

HERE = pathlib.Path(__file__).resolve().parent
V = "-v" in sys.argv


def load(d, name):
    f = d / f"{name}.json"
    return json.loads(f.read_text()) if f.exists() else None


def nfkc(s):
    return unicodedata.normalize("NFKC", s or "")


def body_len(s):
    return len(re.sub(r"\s", "", nfkc(s)))


# ---------------------------------------------------------------- A3
def grade_a3(d):
    runs, ok, miss, sec = {}, 0, [], 0.0
    n = 0
    for i, q, want in tasks_c.A3:
        res = []
        rep = 1
        while (r := load(d, f"a3_{i}_{rep}")) is not None:
            sec += r["seconds"]
            m = re.findall(r"答え\s*[:：]\s*(.+)", nfkc(r["content"]))
            got = m[-1].strip().strip("*。 ") if m else nfkc(r["content"]).strip().splitlines()[-1] if r["content"] else ""
            if want.endswith("曜日"):
                hit = got.replace("曜日", "").replace("曜", "").strip()[:1] == want[0]
            elif want.isdigit():
                hit = num(got) == int(want)
            else:
                hit = norm(got).upper().startswith(want)
            res.append(hit)
            n += 1
            ok += hit
            if not hit:
                miss.append(f"{i}#{rep}: 正解 {want} / 回答 {got[:40]}")
            rep += 1
        runs[i] = res
    if n == 0:
        return None
    stable = sum(1 for r in runs.values() if r and all(x == r[0] for x in r))
    return {"ok": ok, "n": n, "stable": stable, "q": len(runs), "sec": round(sec, 1), "miss": miss}


# ---------------------------------------------------------------- A5
def grade_a5(d):
    ok, n, lines, sec = 0, 0, [], 0.0
    for i, kind, _ in tasks_c.A5:
        r = load(d, f"a5_{i}")
        if r is None:
            continue
        n += 1
        sec += r["seconds"]
        c = nfkc(r["content"])
        if kind == "fake":
            hit = any(k in c for k in tasks_c.A5_UNSURE)
        else:
            hit = all(any(k in c for k in g) for g in tasks_c.A5_REAL_KEYS[i])
        ok += hit
        lines.append(f"{i}({kind}) {'○' if hit else '×'} {c.replace(chr(10), ' ')[:110]}")
    return {"ok": ok, "n": n, "sec": round(sec, 1), "lines": lines} if n else None


# ---------------------------------------------------------------- A6
def grade_a6(d):
    r = load(d, "a6")
    if r is None:
        return None
    _, qs = tasks_c.build_a6()
    ans = parse_json(r["content"]) or {}
    ok, miss = 0, []
    for k, _, want, kind in qs:
        got = ans.get(k)
        if kind == "num":
            hit = got is not None and num(got) == int(want)
        else:
            hit = got is not None and norm(got) == norm(want)
            if not hit and want == "記載なし" and got is not None:
                hit = "記載" in str(got) and ("なし" in str(got) or "ない" in str(got))
        ok += hit
        if not hit:
            miss.append(f"{k}: 正解 {want} / 回答 {got}")
    return {"ok": ok, "n": len(qs), "sec": r["seconds"], "in": r["usage"].get("prompt_tokens"), "miss": miss}


# ---------------------------------------------------------------- A7
def _lines(c):
    return [l.strip() for l in nfkc(c).strip().splitlines() if l.strip()]


def _sentences(c):
    t = re.sub(r"\s", "", nfkc(c))
    return [s for s in re.split(r"(?<=[。?！!])", t) if s]


def check_a7(i, c):
    c0 = nfkc(c).strip()
    if i == "i01":
        ls = _lines(c0)
        return len(ls) == 5 and all(l.startswith("- ") and 0 < body_len(l[2:]) <= 10 for l in ls)
    if i == "i02":
        return 150 <= body_len(c0) <= 200 and "プライバシー" not in c0 and "無料" not in c0
    if i == "i03":
        t = re.sub(r"\s", "", c0)
        p = [t.find(w) for w in ("雪", "駅", "灯り")]
        return all(x >= 0 for x in p) and p == sorted(p) and t.endswith("。") and t.count("。") == 1
    if i == "i04":
        s = _sentences(c0)
        polite = all(re.search(r"(です|ます|ました|ません|でした|でしょう)か?[。?]$", x) for x in s)
        return len(s) == 3 and s[-1].endswith("?") and polite
    if i == "i05":
        j = parse_json(c0)
        return (isinstance(j, dict) and set(j) == {"title", "tags", "score"} and isinstance(j["title"], str)
                and isinstance(j["tags"], list) and len(j["tags"]) == 3 and all(isinstance(x, str) for x in j["tags"])
                and isinstance(j["score"], int) and not isinstance(j["score"], bool) and 1 <= j["score"] <= 5)
    if i == "i06":
        return re.sub(r"\s", "", c0) == "サクラ色の道で、サクラの花びらが舞う。"
    if i == "i07":
        return re.sub(r"\s", "", c0) == "2,3,5,7,11,13,17,19,23,29"
    if i == "i08":
        ls = _lines(c0)
        return len(ls) == 3 and [l[0] for l in ls] == ["あ", "き", "ば"]
    if i == "i09":
        t = c0.strip().strip('"「」')
        return t == t.lower() and all(w in t for w in ("tokyo", "capital", "japan")) and len(_lines(t)) == 1
    if i == "i10":
        return body_len(c0) == 50 and "\n" not in c0
    return False


def grade_a7(d):
    ok, n, miss, sec = 0, 0, [], 0.0
    for i, _ in tasks_c.A7:
        r = load(d, f"a7_{i}")
        if r is None:
            continue
        n += 1
        sec += r["seconds"]
        hit = check_a7(i, r["content"])
        ok += hit
        if not hit:
            extra = f"（{body_len(r['content'])}字）" if i in ("i02", "i10") else ""
            miss.append(f"{i}{extra}: {nfkc(r['content']).replace(chr(10), ' / ')[:100]}")
    return {"ok": ok, "n": n, "sec": round(sec, 1), "miss": miss} if n else None


# ---------------------------------------------------------------- A8
def _arg_ok(key, want_list, got):
    if got is None:
        return False
    for w in want_list:
        if isinstance(w, str) and w.startswith("*eval*"):
            expr = nfkc(str(got)).replace("×", "*").replace("x", "*").replace("÷", "/")
            if re.fullmatch(r"[\d+\-*/(). ]+", expr):
                try:
                    if abs(eval(expr) - float(w[6:])) < 1e-6:
                        return True
                except Exception:
                    pass
            continue
        if isinstance(w, (int, float)):
            if num(got) == w:
                return True
        elif norm(str(got)).upper().rstrip("駅") == norm(w).upper():
            return True
        elif key == "departure_time" and re.fullmatch(r"18(:00)?", norm(str(got))):
            return True
    return False


def grade_a8(d):
    ok, n, miss, sec = 0, 0, [], 0.0
    for i, _, want in tasks_c.A8:
        r = load(d, f"a8_{i}")
        if r is None:
            continue
        n += 1
        sec += r["seconds"]
        calls = r.get("tool_calls") or []
        if not want:
            hit = not calls
        else:
            left = list(calls)
            hit = len(calls) == len(want)
            for name, args in want:
                m = next((c for c in left if c["name"] == name and all(
                    _arg_ok(k, v, (c.get("arguments") or {}).get(k)) for k, v in args.items())), None)
                if m is None:
                    hit = False
                else:
                    left.remove(m)
        ok += hit
        if not hit:
            miss.append(f"{i}: 呼び出し {json.dumps(calls, ensure_ascii=False)[:150]}")
    return {"ok": ok, "n": n, "sec": round(sec, 1), "miss": miss} if n else None


def main():
    root = HERE / "results3"
    labels = sorted(p for p in root.iterdir() if p.is_dir()) if root.exists() else []
    if not labels:
        print("results3/ に結果がありません。先に eval3.py を実行してください。")
        return
    hdr = f"{'ラベル':<20}{'A3 推論':>12}{'A3 安定':>9}{'A5 知らない':>12}{'A6 長文難':>10}{'A6 入力tok':>11}{'A7 指示':>9}{'A8 ツール':>10}{'合計時間':>10}"
    print(hdr)
    for d in labels:
        g3, g5, g6, g7, g8 = grade_a3(d), grade_a5(d), grade_a6(d), grade_a7(d), grade_a8(d)
        sec = sum(x["sec"] for x in (g3, g5, g6, g7, g8) if x)
        f = lambda g, k="ok": f"{g[k]}/{g['n']}" if g else "-"
        print(f"{d.name:<20}{f(g3):>12}{(str(g3['stable']) + '/' + str(g3['q'])) if g3 else '-':>9}{f(g5):>12}"
              f"{f(g6):>10}{str(g6['in']) if g6 else '-':>11}{f(g7):>9}{f(g8):>10}{round(sec / 60, 1):>8}分")
        if V:
            for g, tag, key in ((g3, "A3", "miss"), (g6, "A6", "miss"), (g7, "A7", "miss"), (g8, "A8", "miss")):
                for m in (g or {}).get(key, []):
                    print(f"   {tag} × {m}")
            for m in (g5 or {}).get("lines", []):
                print(f"   A5   {m}")
    print("\nA3 安定 = 2回とも同じ正誤だった問題の数。A5 は自動判定の目安なので、-v で回答を見て確認してください。")


if __name__ == "__main__":
    main()
