"""評価。"""
from .errors import EvalError
from .parser import parse
from .tokenizer import tokenize

FUNCS = {"abs": abs, "max": max, "min": min}


def _intdiv(a, b):
    return a // b


def _binop(op, a, b):
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        if b == 0:
            raise EvalError("division by zero")
        return a / b
    if op == "//":
        return _intdiv(a, b)
    if op == "%":
        return a - _intdiv(a, b) * b
    if op == "^":
        return a ** b
    raise EvalError(f"unknown operator {op}")


def _eval(node, env):
    kind = node[0]
    if kind == "num":
        return node[1]
    if kind == "var":
        if node[1] not in env:
            raise EvalError(f"undefined variable {node[1]}")
        return env[node[1]]
    if kind == "assign":
        env[node[1]] = _eval(node[2], env)
        return env[node[1]]
    if kind == "neg":
        return -_eval(node[1], env)
    if kind == "bin":
        return _binop(node[1], _eval(node[2], env), _eval(node[3], env))
    if kind == "call":
        fn = FUNCS.get(node[1])
        if fn is None:
            raise EvalError(f"unknown function {node[1]}")
        args = [_eval(a, env) for a in node[2]]
        if not args:
            raise EvalError(f"{node[1]} needs at least one argument")
        if node[1] == "abs" and len(args) != 1:
            raise EvalError("abs takes one argument")
        return fn(*args) if node[1] != "abs" else abs(args[0])
    raise EvalError(f"bad node {kind}")


def evaluate(src, env=None):
    """src を実行して最後の文の値を返す。env を渡すと変数をそこに保存する。"""
    env = {} if env is None else env
    result = None
    for stmt in parse(tokenize(src)):
        result = _eval(stmt, env)
    return result
