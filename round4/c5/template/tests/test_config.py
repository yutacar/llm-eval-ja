import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

from mdlint import cli, config
from mdlint.errors import ConfigError


def run(args):
    out, err = StringIO(), StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = cli.main(args)
    return code, out.getvalue(), err.getvalue()


class ConfigTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def write(self, text):
        p = os.path.join(self.dir, ".mdlint.toml")
        with open(p, "w") as f:
            f.write(text)
        return p

    def test_defaults(self):
        self.assertEqual(config.load(None)["indent_size"], 2)

    def test_file_and_override(self):
        p = self.write("indent_size = 4\n")
        self.assertEqual(config.load(p)["indent_size"], 4)
        self.assertEqual(config.load(p, {"indent_size": 3})["indent_size"], 3)

    def test_invalid(self):
        with self.assertRaises(ConfigError):
            config.load(self.write("indent_size = 0\n"))
        with self.assertRaises(ConfigError):
            config.load(self.write("nosuch = 1\n"))

    def test_print_config(self):
        code, out, _ = run(["--config", self.write("indent_size = 4\n"), "--print-config"])
        self.assertEqual((code, json.loads(out)["indent_size"]), (0, 4))

    def test_cli_error(self):
        code, _, err = run(["--config", self.write("indent_size = 99\n"), "--print-config"])
        self.assertEqual(code, 2)
        self.assertIn("indent_size", err)
