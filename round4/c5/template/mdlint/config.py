"""設定の読み込み。優先順位: 既定値 < 設定ファイル（.mdlint.toml）< コマンドラインの引数。"""
import os
import tomllib

from .errors import ConfigError

DEFAULTS = {
    "disable": [],               # 使わない規則（例: ["MD013"]）
    "heading_style": "atx",      # 見出しの書き方（atx / setext）
    "indent_size": 2,            # リストの字下げの幅
    "allow_trailing_spaces": False,
}


def _check_disable(v):
    if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
        raise ConfigError("disable must be a list of rule ids")


def _check_heading_style(v):
    if v not in ("atx", "setext"):
        raise ConfigError("heading_style must be 'atx' or 'setext'")


def _check_indent_size(v):
    if not isinstance(v, int) or isinstance(v, bool) or not 1 <= v <= 8:
        raise ConfigError("indent_size must be an integer from 1 to 8")


def _check_allow_trailing_spaces(v):
    if not isinstance(v, bool):
        raise ConfigError("allow_trailing_spaces must be true or false")


VALIDATORS = {
    "disable": _check_disable,
    "heading_style": _check_heading_style,
    "indent_size": _check_indent_size,
    "allow_trailing_spaces": _check_allow_trailing_spaces,
}


def find_config(start="."):
    d = os.path.abspath(start)
    while True:
        p = os.path.join(d, ".mdlint.toml")
        if os.path.isfile(p):
            return p
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def load(path=None, overrides=None):
    cfg = dict(DEFAULTS)
    if path:
        with open(path, "rb") as f:
            data = tomllib.load(f)
        for k, v in data.items():
            if k not in DEFAULTS:
                raise ConfigError(f"unknown option: {k}")
            cfg[k] = v
    for k, v in (overrides or {}).items():
        if v is not None:
            cfg[k] = v
    for k, check in VALIDATORS.items():
        check(cfg[k])
    return cfg
