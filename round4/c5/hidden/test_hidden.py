import json
import os
import re
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

from mdlint import cli, config
from mdlint.errors import ConfigError
from mdlint.runner import lint_text


def run(args):
    out, err = StringIO(), StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = cli.main(args)
        except SystemExit as e:
            code = e.code
    return code, out.getvalue(), err.getvalue()


def md013(src, cfg):
    return [p for p in lint_text(src, cfg) if p["rule"] == "MD013"]


class MaxLineLengthTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def write(self, text, name=".mdlint.toml"):
        p = os.path.join(self.dir, name)
        with open(p, "w") as f:
            f.write(text)
        return p

    def test_default(self):
        cfg = config.load(None)
        self.assertEqual(cfg["max_line_length"], 80)
        self.assertEqual(len(md013("# T\n\n" + "a" * 81 + "\n", cfg)), 1)
        self.assertEqual(len(md013("# T\n\n" + "a" * 80 + "\n", cfg)), 0)

    def test_file(self):
        cfg = config.load(self.write("max_line_length = 120\n"))
        self.assertEqual(cfg["max_line_length"], 120)
        self.assertEqual(md013("# T\n\n" + "a" * 120 + "\n", cfg), [])
        probs = md013("# T\n\n" + "a" * 121 + "\n", cfg)
        self.assertEqual(len(probs), 1)
        self.assertIn("line too long (121 > 120)", probs[0]["message"])

    def test_fullwidth_and_code(self):
        cfg = config.load(self.write("max_line_length = 30\n"))
        self.assertEqual(len(md013("# T\n\n" + "あ" * 16 + "\n", cfg)), 1)
        self.assertEqual(md013("# T\n\n```\n" + "a" * 50 + "\n```\n", cfg), [])

    def test_validation(self):
        for v in ["19", "401", "true", "\"100\"", "80.5"]:
            with self.subTest(v=v):
                with self.assertRaises(ConfigError) as cm:
                    config.load(self.write(f"max_line_length = {v}\n"))
                self.assertIn("max_line_length", str(cm.exception))
        for v in ["20", "400"]:
            with self.subTest(v=v):
                self.assertEqual(config.load(self.write(f"max_line_length = {v}\n"))["max_line_length"], int(v))

    def test_cli_override(self):
        p = self.write("max_line_length = 120\n")
        code, out, _ = run(["--config", p, "--max-line-length", "100", "--print-config"])
        self.assertEqual((code, json.loads(out)["max_line_length"]), (0, 100))
        code, out, _ = run(["--config", p, "--print-config"])
        self.assertEqual(json.loads(out)["max_line_length"], 120)

    def test_cli_lint(self):
        md = self.write("# T\n\n" + "a" * 90 + "\n", "doc.md")
        self.assertEqual(run([md, "--max-line-length", "100"])[0], 0)
        code, out, _ = run([md, "--max-line-length", "85"])
        self.assertEqual(code, 1)
        self.assertIn("line too long (90 > 85)", out)

    def test_cli_error(self):
        code, _, err = run(["--max-line-length", "5", "--print-config"])
        self.assertEqual(code, 2)
        self.assertIn("max_line_length", err)

    def test_help(self):
        code, out, _ = run(["--help"])
        self.assertIn("--max-line-length", out)

    def test_docs(self):
        doc = open(os.path.join("docs", "config.md"), encoding="utf-8").read()
        row = next((l for l in doc.splitlines() if "max_line_length" in l and l.startswith("|")), "")
        self.assertTrue(row, "docs/config.md の表に max_line_length の行がない")
        self.assertIn("80", row)
        self.assertIn("--max-line-length", row)

    def test_existing_options_still_work(self):
        cfg = config.load(self.write("indent_size = 4\nmax_line_length = 100\n"))
        self.assertEqual((cfg["indent_size"], cfg["max_line_length"]), (4, 100))
        with self.assertRaises(ConfigError):
            config.load(self.write("nosuch = 1\n"))


if __name__ == "__main__":
    unittest.main()
