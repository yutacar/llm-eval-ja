#!/usr/bin/env python3
"""unittest を実行して、subTest も1件ずつ数えて JSON で出す。  例: python3 count_tests.py tests.test_hidden"""
import json
import os
import sys
import unittest


class Counter(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.items, self.with_sub = [], set()

    def addSubTest(self, test, sub, err):
        self.with_sub.add(test.id())
        self.items.append((f"{test._testMethodName} {sub._subDescription()}", err is None))

    def addSuccess(self, test):
        if test.id() not in self.with_sub:
            self.items.append((test.id().split(".")[-1], True))

    def addFailure(self, test, err):
        self.items.append((test.id().split(".")[-1], False))

    def addError(self, test, err):
        self.items.append((test.id().split(".")[-1], False))


def main():
    sys.path.insert(0, os.getcwd())
    suite = unittest.defaultTestLoader.loadTestsFromNames(sys.argv[1:])
    r = Counter()
    suite.run(r)
    print(json.dumps({"passed": sum(ok for _, ok in r.items), "total": len(r.items),
                      "failed": [n for n, ok in r.items if not ok]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
