#!/usr/bin/env python3
"""第4回（OpenCode・C1〜C5）の採点。~/work/c1-<ラベル> 〜 c5-<ラベル> を全部探して表にする。

  python3 grade_d.py            # 表だけ
  python3 grade_d.py -v         # 落ちたテストの名前・変えたファイルも表示
  python3 grade_d.py ud-iq4_xs  # ラベルを指定

採点は作業フォルダのコピーで行う（作業フォルダは変更しない）。守るべきファイル（tests/ など）は元に戻してから検査し、
書き換えられていたら「改変」と表示する。
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
WORK = pathlib.Path.home() / "work"
COUNT = HERE / "tools" / "count_tests.py"
TASKS = ["c1", "c2", "c3", "c4", "c5"]
NAMES = {"c1": "C1 仕様変更", "c2": "C2 原因調査", "c3": "C3 日本語", "c4": "C4 セキュリティ", "c5": "C5 設定追加"}
# 課題ごとに、変えてはいけないファイル（テンプレートからの相対パス）
PROTECTED = {
    "c1": [],
    "c2": ["tests/test_bookings.py", "run_ci.sh", "ci-failure.log"],
    "c3": ["tests/test_jpdata.py", "SPEC.md"],
    "c4": ["tests/test_app.py", "tests/helper.py"],
    "c5": ["tests/test_rules.py", "tests/test_config.py"],
}
# 隠しテストの件数（import に失敗して1件しか数えられなかったときも、この数で割る）
EXPECTED = {"c1": 21, "c2": 24, "c3": 90, "c4": 20, "c5": 16}
IGNORE = {".git", "__pycache__", "opencode.log", "time.txt", ".pytest_cache"}
V = "-v" in sys.argv


def count(cwd, names, env=None):
    e = dict(os.environ, **(env or {}))
    try:
        p = subprocess.run([sys.executable, str(COUNT), *names], cwd=cwd, capture_output=True, text=True, timeout=300, env=e)
        line = next((l for l in reversed(p.stdout.splitlines()) if l.startswith("{")), None)
        return json.loads(line) if line else {"passed": 0, "total": 0, "failed": ["(実行できず)"]}
    except subprocess.TimeoutExpired:
        return {"passed": 0, "total": 0, "failed": ["(5分で打ち切り)"]}


def copy_work(src, dst):
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*IGNORE))


def files(root):
    out = {}
    for p in root.rglob("*"):
        if p.is_file() and not (set(p.relative_to(root).parts) & IGNORE):
            out[str(p.relative_to(root))] = p.read_bytes()
    return out


def changes(task, d):
    tpl, got = files(HERE / task / "template"), files(d)
    changed = sorted(k for k in tpl.keys() | got.keys() if tpl.get(k) != got.get(k))
    tampered = [k for k in PROTECTED[task] if tpl.get(k) != got.get(k)]
    return changed, tampered


def restore(task, t):
    for rel in PROTECTED[task]:
        shutil.copy(HERE / task / "template" / rel, t / rel)


def add_hidden(task, t):
    shutil.copy(HERE / task / "hidden" / "test_hidden.py", t / "tests" / "test_hidden.py")


def grade(task, d):
    res = {"extra": []}
    with tempfile.TemporaryDirectory() as tmp:
        t = pathlib.Path(tmp) / "w"
        copy_work(d, t)
        restore(task, t)
        add_hidden(task, t)
        if task == "c1":
            res["hidden"] = count(t, ["tests.test_hidden"])
            own = count(t, ["tests.test_shop"])
            res["extra"].append(f"自分で直したテスト {own['passed']}/{own['total']}")
        elif task == "c2":
            a = count(t, ["tests.test_hidden"], {"TZ": "UTC", "GRADER_TZ": "UTC"})
            b = count(t, ["tests.test_hidden"], {"TZ": "America/Los_Angeles", "GRADER_TZ": "America/Los_Angeles"})
            res["hidden"] = {"passed": a["passed"] + b["passed"], "total": a["total"] + b["total"],
                             "failed": [f"UTC:{x}" for x in a["failed"]] + [f"LA:{x}" for x in b["failed"]]}
            ci = count(t, ["tests.test_bookings"], {"TZ": "UTC"})
            res["extra"].append(f"CI のテスト(UTC) {ci['passed']}/{ci['total']}")
        elif task == "c3":
            res["hidden"] = count(t, ["tests.test_hidden"])
            o = count(t, ["tests.test_jpdata"])
            res["extra"].append(f"元のテスト {o['passed']}/{o['total']}")
        elif task == "c4":
            res["hidden"] = count(t, ["tests.test_hidden"])
            o = count(t, ["tests.test_app"])
            res["extra"].append(f"元のテスト {o['passed']}/{o['total']}")
            if (t / "tests" / "test_security.py").exists():
                own = count(t, ["tests.test_security"])
                # 自作の攻撃テストを、直す前のコードで動かす（失敗すれば穴を突けている）
                u = pathlib.Path(tmp) / "orig"
                shutil.copytree(HERE / task / "template", u)
                shutil.copy(t / "tests" / "test_security.py", u / "tests")
                before = count(u, ["tests.test_security"])
                res["extra"].append(f"自作の攻撃テスト {own['total']}件（直した後に通る {own['passed']}、直す前に落ちる {before['total'] - before['passed']}）")
            else:
                res["extra"].append("自作の攻撃テストなし")
        elif task == "c5":
            res["hidden"] = count(t, ["tests.test_hidden"])
            o = count(t, ["tests.test_rules", "tests.test_config"])
            res["extra"].append(f"元のテスト {o['passed']}/{o['total']}")
            res["extra"].append("tests/test_max_line_length.py " + ("あり" if (t / "tests" / "test_max_line_length.py").exists() else "なし"))
    return res


def run_info(d):
    f = d / "time.txt"
    if not f.exists():
        return None, None
    s = f.read_text()
    sec = re.search(r"（(\d+) 秒）", s) or re.search(r"所要 (\d+) 分", s)
    mins = round(int(sec[1]) / 60, 1) if sec and "秒" in sec[0] else (int(sec[1]) if sec else None)
    rc = re.search(r"終了コード (\d+)", s)
    return mins, (int(rc[1]) if rc else None)


def labels():
    want = [a for a in sys.argv[1:] if not a.startswith("-")]
    if want:
        return want
    found = set()
    for p in WORK.glob("c[1-5]-*"):
        if p.is_dir() and (p / ".git").exists():
            found.add(p.name.split("-", 1)[1])
    return sorted(found)


def main():
    labs = labels()
    if not labs:
        print("~/work/c1-<ラベル> などの作業フォルダが見つかりません。")
        return
    table = {}
    for lab in labs:
        print(f"===== {lab}")
        for task in TASKS:
            d = WORK / f"{task}-{lab}"
            if not d.exists():
                continue
            mins, rc = run_info(d)
            r = grade(task, d)
            changed, tampered = changes(task, d)
            h = r["hidden"]
            if h["total"] < EXPECTED[task]:
                h["total"] = EXPECTED[task]
            note = []
            if rc == 124:
                note.append("時間切れ")
            elif rc is None:
                note.append("未実行")
            if tampered:
                note.append("改変:" + ",".join(tampered))
            table[(lab, task)] = (h["passed"], h["total"], mins, note)
            pct = f"{h['passed'] / h['total'] * 100:.0f}%" if h["total"] else "-"
            print(f"  {NAMES[task]:<10} 隠しテスト {h['passed']:>3}/{h['total']:<3} ({pct:>4})  "
                  f"{(str(mins) + '分') if mins is not None else '-':>7}  " + "  ".join(r["extra"] + note))
            if V:
                for x in h["failed"][:30]:
                    print(f"      × {x}")
                print(f"      変えたファイル {len(changed)}: {', '.join(changed[:15])}{' …' if len(changed) > 15 else ''}")
    print("\n===== まとめ（隠しテストの通過率 / 所要時間）")
    print(f"{'ラベル':<16}" + "".join(f"{NAMES[t]:>16}" for t in TASKS) + f"{'合計':>10}")
    for lab in labs:
        cells, ok, tot = [], 0, 0
        for task in TASKS:
            v = table.get((lab, task))
            if not v:
                cells.append(f"{'-':>16}")
                continue
            p, n, m, note = v
            ok += p / n if n else 0
            tot += 1
            mark = "*" if note else ""
            cells.append(f"{(f'{p / n * 100:.0f}%' if n else '-') + mark:>9} {(f'{m:.0f}分' if m is not None else '-'):>5}")
        print(f"{lab:<16}" + "".join(cells) + f"{(f'{ok / tot * 100:.0f}%' if tot else '-'):>10}")
    print("\n* = 時間切れ・未実行・守るべきファイルの改変のどれかあり（上の詳細を参照）。合計は5課題の通過率の平均。")


if __name__ == "__main__":
    main()
