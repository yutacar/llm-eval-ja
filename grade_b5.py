#!/usr/bin/env python3
"""B5（難しいバグ修正：電卓言語）の採点。作業フォルダのコードを、元のテスト＋隠しテストで別の場所で検査する。

例:  python3 grade_b5.py ~/work/b5-ud-iq4_xs
"""
import filecmp, pathlib, re, shutil, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE / "b5" / "template"
HIDDEN = HERE / "b5" / "hidden" / "test_hidden.py"


def run_tests(code_dir, only_hidden=False):
    with tempfile.TemporaryDirectory() as t:
        t = pathlib.Path(t)
        shutil.copytree(code_dir / "minical", t / "minical")
        if only_hidden:
            (t / "tests").mkdir()
            (t / "tests" / "__init__.py").write_text("")
            shutil.copy(HIDDEN, t / "tests")
        else:
            shutil.copytree(TEMPLATE / "tests", t / "tests")       # 元のテスト（手を加えられていても元に戻して検査）
        p = subprocess.run([sys.executable, "-m", "unittest", "-v"], cwd=t, capture_output=True, text=True, timeout=120)
        out = p.stderr
        total = int(m.group(1)) if (m := re.search(r"Ran (\d+) test", out)) else 0
        bad = sum(int(x) for x in re.findall(r"(?:failures|errors)=(\d+)", out))
        fails = re.findall(r"^(?:FAIL|ERROR): (\w+) \(([\w.]+)", out, re.M)
        return total - bad, total, fails


def main():
    if len(sys.argv) != 2:
        print("使い方: python3 grade_b5.py <作業フォルダ>")
        sys.exit(1)
    d = pathlib.Path(sys.argv[1]).expanduser()
    ok1, n1, f1 = run_tests(d)
    ok2, n2, f2 = run_tests(d, only_hidden=True)
    cmp = filecmp.dircmp(TEMPLATE / "tests", d / "tests") if (d / "tests").exists() else None
    touched = bool(cmp and (cmp.diff_files or cmp.left_only or cmp.right_only))
    print(f"作業フォルダ: {d}")
    print(f"元のテスト      : {ok1}/{n1} 通過")
    for name, _ in f1:
        print(f"   × {name}")
    print(f"隠しテスト      : {ok2}/{n2} 通過（テストの値だけに合わせた直し方を見つけるためのもの）")
    for name, _ in f2:
        print(f"   × {name}")
    print(f"tests/ の変更   : {'あり（ルール違反）' if touched else 'なし'}")
    if (d / ".git").exists():
        st = subprocess.run(["git", "diff", "--shortstat", "HEAD", "--", "minical"], cwd=d,
                            capture_output=True, text=True).stdout.strip()
        print(f"minical の変更 : {st or '変更なし'}")


if __name__ == "__main__":
    main()
