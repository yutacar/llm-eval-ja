"""決済の記録（テストでは毎回 reset() で空にする）。"""
_entries = []


def record(entry):
    _entries.append(dict(entry))


def entries():
    return [dict(e) for e in _entries]


def reset():
    _entries.clear()
