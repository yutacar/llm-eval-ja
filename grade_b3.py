#!/usr/bin/env python3
"""B3（コードを読んで答える）の採点。ANSWERS.md の各問にキーワードがあるかを見る（最後は目で確認）。

例:  python3 grade_b3.py ~/work/b3-ud-iq4_xs
"""
import base64, json, pathlib, re, subprocess, sys

KEY = json.loads(base64.b64decode("eyJRMSI6IFtbIjgwOTUiXSwgWyI4MDgwIl1dLCAiUTIiOiBbWyJ4LWFwaS1rZXkiXSwgWyJCZWFyZXIiLCAiQXV0aG9yaXphdGlvbiJdLCBbIlNUUkFUQV9BUElfS0VZIl1dLCAiUTMiOiBbWyJwcmVmaWxsLmNwcCJdLCBbIuOCquODlSIsICLnhKHlirkiLCAib2ZmIiwgIk9GRiIsICJPZmYiLCAi5q2iIiwgIuS9v+OCj+OBquOBhCIsICLjgZfjgarjgYQiLCAi54Sh44GXIiwgIuOBquOBlyIsICJkaXNhYmxlIl1dLCAiUTQiOiBbWyI3MDAiXSwgWyJnZW5lcmF0ZS5jcHAiXV0sICJRNSI6IFtbImFudGhyb3BpY190b19tZXNzYWdlcyJdLCBbImZyb250ZW5kLnB5Il0sIFsi44Oq44Kv44Ko44K544OIIiwgInJlcXVlc3QiLCAicmVhc29uaW5nX2J1ZGdldF90b2tlbnMg44Gu5pa5IiwgInJlYXNvbmluZ19idWRnZXRfdG9rZW5z44GM5YSq5YWIIiwgInJlYXNvbmluZ19idWRnZXRfdG9rZW5zIOOBjOWEquWFiCJdXX0="))
NOTE = {"Q5": "優先されるのは「リクエスト側の reasoning_budget_tokens」。3つ目の点は目で確認してください"}


def main():
    if len(sys.argv) != 2:
        print("使い方: python3 grade_b3.py <作業フォルダ>")
        sys.exit(1)
    d = pathlib.Path(sys.argv[1]).expanduser()
    f = d / "ANSWERS.md"
    if not f.exists():
        print("ANSWERS.md がありません")
        sys.exit(1)
    text = f.read_text()
    parts = {m.group(1): m.group(2) for m in re.finditer(r"#+\s*(Q\d)\s*\n(.*?)(?=\n#+\s*Q\d|\Z)", text, re.S)}
    total = got = 0
    for q, groups in KEY.items():
        body = parts.get(q, "")
        hits = [any(k in body for k in g) for g in groups]
        total += len(groups)
        got += sum(hits)
        mark = "○" if all(hits) else ("△" if any(hits) else "×")
        print(f"{q} {mark} {sum(hits)}/{len(groups)}  " + " / ".join(body.strip().splitlines()[:2])[:160])
        if q in NOTE:
            print("    ※", NOTE[q])
    print(f"合計: {got}/{total} 点")
    if (d / ".git").exists():
        st = subprocess.run(["git", "status", "--porcelain"], cwd=d, capture_output=True, text=True).stdout.split("\n")
        other = [l for l in st if l.strip() and not l.endswith(("ANSWERS.md", "opencode.log", "time.txt"))]
        print("ANSWERS.md 以外の変更:", "なし" if not other else f"{len(other)} 件（ルール違反）")


if __name__ == "__main__":
    main()
