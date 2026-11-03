"""規則の一覧。新しい規則はここの ALL に足す。"""
import importlib

IDS = [f"MD{n:03d}" for n in range(1, 37)]
ALL = [importlib.import_module(f".{i.lower()}", __name__) for i in IDS]


def enabled(cfg):
    off = {x.upper() for x in cfg.get("disable", [])}
    return [r for r in ALL if r.ID not in off]
