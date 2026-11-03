import unittest

from mdlint import config
from mdlint.runner import lint_text


def ids(src, **cfg):
    return [(p["line"], p["rule"]) for p in lint_text(src, config.load(None, cfg))]


class RulesTest(unittest.TestCase):
    def test_clean(self):
        self.assertEqual(ids("# Title\n\nHello.\n"), [])

    def test_md013(self):
        self.assertIn((3, "MD013"), ids("# T\n\n" + "a" * 81 + "\n"))
        self.assertNotIn((3, "MD013"), ids("# T\n\n" + "a" * 80 + "\n"))

    def test_md013_fullwidth(self):
        self.assertIn((3, "MD013"), ids("# T\n\n" + "あ" * 41 + "\n"))

    def test_md013_code_block(self):
        self.assertEqual(ids("# T\n\n```\n" + "a" * 120 + "\n```\n"), [])

    def test_md007_indent(self):
        self.assertIn((4, "MD007"), ids("# T\n\n- a\n   - b\n"))
        self.assertEqual(ids("# T\n\n- a\n    - b\n", indent_size=4), [])

    def test_md009(self):
        self.assertIn((3, "MD009"), ids("# T\n\nx  \n"))
        self.assertEqual(ids("# T\n\nx  \n", allow_trailing_spaces=True), [])
