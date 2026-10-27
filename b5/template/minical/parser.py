"""構文解析。式を入れ子のタプル（構文木）にする。

("num", v) / ("var", name) / ("assign", name, expr) / ("neg", expr) / ("bin", op, left, right) / ("call", name, [args])
"""
from .errors import EvalError


class Parser:
    def __init__(self, tokens):
        self.t = tokens
        self.i = 0

    def peek(self):
        return self.t[self.i]

    def take(self):
        tok = self.t[self.i]
        self.i += 1
        return tok

    def expect(self, value):
        tok = self.take()
        if tok != ("OP", value):
            raise EvalError(f"expected {value!r}, got {tok[1]!r}")
        return tok

    def program(self):
        stmts = []
        while self.peek()[0] != "END":
            if self.peek() == ("OP", ";"):
                self.take()
                continue
            stmts.append(self.statement())
            if self.peek()[0] != "END":
                self.expect(";")
        return stmts

    def statement(self):
        if self.peek()[0] == "NAME" and self.t[self.i + 1] == ("OP", "="):
            name = self.take()[1]
            self.take()
            return ("assign", name, self.expr())
        return self.expr()

    def expr(self):                       # + -
        node = self.term()
        while self.peek() in (("OP", "+"), ("OP", "-")):
            op = self.take()[1]
            node = ("bin", op, node, self.term())
        return node

    def term(self):                       # * / // %
        node = self.power()
        while self.peek() in (("OP", "*"), ("OP", "/"), ("OP", "//"), ("OP", "%")):
            op = self.take()[1]
            node = ("bin", op, node, self.power())
        return node

    def power(self):                      # ^
        node = self.unary()
        while self.peek() == ("OP", "^"):
            self.take()
            node = ("bin", "^", node, self.unary())
        return node

    def unary(self):                      # 単項 - +
        if self.peek() == ("OP", "-"):
            self.take()
            return ("neg", self.unary())
        if self.peek() == ("OP", "+"):
            self.take()
            return self.unary()
        return self.atom()

    def atom(self):
        kind, val = self.take()
        if kind == "NUM":
            return ("num", val)
        if kind == "NAME":
            if self.peek() == ("OP", "("):
                self.take()
                args = []
                if self.peek() != ("OP", ")"):
                    args.append(self.expr())
                    if self.peek() == ("OP", ","):
                        self.take()
                        args.append(self.expr())
                self.expect(")")
                return ("call", val, args)
            return ("var", val)
        if (kind, val) == ("OP", "("):
            node = self.expr()
            self.expect(")")
            return node
        raise EvalError(f"unexpected token {val!r}")


def parse(tokens):
    return Parser(tokens).program()
