"""字句解析。"""
import re

from .errors import EvalError

TOKEN_RE = re.compile(r"""
    (?P<NUM>\d+(?:\.\d+)?)
  | (?P<NAME>[A-Za-z_]+)
  | (?P<OP>//|[-+*/%^(),=;])
  | (?P<NL>\n)
  | (?P<WS>[ \t\r]+)
""", re.X)


def tokenize(src):
    """(種類, 値) のリストを返す。種類は NUM / NAME / OP / END。改行は ';' として扱う。"""
    out, pos = [], 0
    while pos < len(src):
        m = TOKEN_RE.match(src, pos)
        if not m:
            raise EvalError(f"unexpected character {src[pos]!r} at {pos}")
        kind, text = m.lastgroup, m.group()
        pos = m.end()
        if kind == "WS":
            continue
        if kind == "NL":
            out.append(("OP", ";"))
        elif kind == "NUM":
            out.append(("NUM", float(text) if "." in text else int(text)))
        else:
            out.append((kind, text))
    out.append(("END", None))
    return out
