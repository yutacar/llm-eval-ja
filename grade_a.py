#!/usr/bin/env python3
"""A1（長文読解）と A4（JSON 抽出）を自動採点し、results/ の全ラベルを並べて表示する。

例:  python3 grade_a.py            # 全ラベル
     python3 grade_a.py -v         # 間違えた問題も表示
"""
import json, pathlib, re, sys, unicodedata
import tasks_a

HERE = pathlib.Path(__file__).resolve().parent
VERBOSE = "-v" in sys.argv


def norm(s):
    s = unicodedata.normalize("NFKC", str(s)).strip()
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"^(No\.?|#)", "", s, flags=re.I)
    s = s[:-1] if s.endswith("様") and len(s) > 1 else s
    return s.rstrip("駅") if s.endswith("駅") and len(s) > 1 else s


def num(s):
    m = re.search(r"-?\d[\d,]*", unicodedata.normalize("NFKC", str(s)))
    return int(m.group().replace(",", "")) if m else None


def parse_json(text):
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", t, re.S)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                return None
    return None


def same(want, got):
    if isinstance(want, int):
        return num(got) == want if got is not None else False
    w, g = norm(want), norm(got)
    if re.fullmatch(r"[\d:-]+", w):                 # 日付・時刻は完全一致
        return w == g
    return bool(g) and (w == g or w in g or g in w)


def grade_a1(d):
    f = d / "a1.json"
    if not f.exists():
        return None
    r = json.loads(f.read_text())
    _, qs = tasks_a.build_a1()
    ans = parse_json(r["content"]) or {}
    ok, miss = 0, []
    for k, _, want, kind in qs:
        got = ans.get(k)
        hit = (num(got) == int(want)) if kind == "num" and got is not None else (got is not None and norm(got) == norm(want))
        if not hit and kind == "text" and want == "記載なし" and got is not None:
            hit = "記載" in str(got) and ("なし" in str(got) or "ない" in str(got))
        ok += hit
        if not hit:
            miss.append(f"{k}: 正解 {want} / 回答 {got}")
    return {"score": ok, "n": len(qs), "sec": r["seconds"], "in": r["usage"].get("prompt_tokens"), "miss": miss}


def grade_a4(d):
    parsed = fields = ok = 0
    sec = 0.0
    miss = []
    n = 0
    for cid, _, _, want in tasks_a.A4:
        f = d / f"a4_{cid}.json"
        if not f.exists():
            continue
        n += 1
        r = json.loads(f.read_text())
        sec += r["seconds"]
        got = parse_json(r["content"])
        if isinstance(got, dict):
            parsed += 1
        else:
            got = {}
            miss.append(f"{cid}: JSON として読めない")
        for k, w in want.items():
            if k == "items":
                gi = got.get("items") if isinstance(got.get("items"), list) else []
                for idx, wi in enumerate(w):
                    g = gi[idx] if idx < len(gi) and isinstance(gi[idx], dict) else {}
                    for kk, ww in wi.items():
                        fields += 1
                        if same(ww, g.get(kk)):
                            ok += 1
                        else:
                            miss.append(f"{cid}.items[{idx}].{kk}: 正解 {ww} / 回答 {g.get(kk)}")
                fields += 1                               # 余計な品目が無いこと
                if len(gi) == len(w):
                    ok += 1
                else:
                    miss.append(f"{cid}.items: 品目数 正解 {len(w)} / 回答 {len(gi)}")
            else:
                fields += 1
                if same(w, got.get(k)):
                    ok += 1
                else:
                    miss.append(f"{cid}.{k}: 正解 {w} / 回答 {got.get(k)}")
    if n == 0:
        return None
    return {"n": n, "parsed": parsed, "fields": fields, "ok": ok, "sec": round(sec, 1), "miss": miss}


def main():
    root = HERE / "results"
    labels = sorted(p for p in root.iterdir() if p.is_dir()) if root.exists() else []
    if not labels:
        print("results/ に結果がありません。先に eval2.py を実行してください。")
        return
    print(f"{'ラベル':<22}{'A1 正解':>10}{'A1 時間':>10}{'A1 入力tok':>12}{'A4 JSON可':>12}{'A4 項目正解':>14}{'A4 時間':>10}")
    for d in labels:
        a1, a4 = grade_a1(d), grade_a4(d)
        c1 = f"{a1['score']}/{a1['n']}" if a1 else "-"
        t1 = f"{a1['sec']}s" if a1 else "-"
        i1 = str(a1["in"]) if a1 else "-"
        c4 = f"{a4['parsed']}/{a4['n']}" if a4 else "-"
        f4 = f"{a4['ok']}/{a4['fields']} ({a4['ok'] * 100 // max(a4['fields'], 1)}%)" if a4 else "-"
        t4 = f"{a4['sec']}s" if a4 else "-"
        print(f"{d.name:<22}{c1:>10}{t1:>10}{i1:>12}{c4:>12}{f4:>14}{t4:>10}")
        if VERBOSE:
            for m in (a1 or {}).get("miss", []):
                print("   A1 ×", m)
            for m in (a4 or {}).get("miss", []):
                print("   A4 ×", m)


if __name__ == "__main__":
    main()
