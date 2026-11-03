from . import rules
from .utils import paths, text


def lint_text(src, cfg, filename="<text>"):
    lines = text.split_lines(src)
    out = []
    for rule in rules.enabled(cfg):
        for lineno, msg in rule.check(lines, cfg):
            out.append({"file": filename, "line": lineno, "rule": rule.ID, "message": msg})
    return sorted(out, key=lambda p: (p["file"], p["line"], p["rule"]))


def run(targets, cfg):
    out = []
    for path in paths.markdown_files(targets):
        with open(path, encoding="utf-8") as f:
            out += lint_text(f.read(), cfg, path)
    return out
