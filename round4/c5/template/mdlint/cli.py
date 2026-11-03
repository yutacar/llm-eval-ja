import argparse
import json
import sys

from . import __version__, config, runner, report
from .errors import ConfigError


def build_parser():
    p = argparse.ArgumentParser(prog="mdlint", description="Markdown の書き方を検査する")
    p.add_argument("paths", nargs="*", help="検査するファイルかフォルダ")
    p.add_argument("--config", help="設定ファイル（省略時は .mdlint.toml を探す）")
    p.add_argument("--disable", help="使わない規則をカンマ区切りで（例: MD013,MD041）")
    p.add_argument("--indent-size", type=int, help="リストの字下げの幅（設定ファイルの indent_size より優先）")
    p.add_argument("--format", choices=["text", "json"], default="text", help="結果の出し方")
    p.add_argument("--print-config", action="store_true", help="使われる設定を JSON で表示して終わる")
    p.add_argument("--version", action="version", version=f"mdlint {__version__}")
    return p


def main(argv=None):
    a = build_parser().parse_args(argv)
    overrides = {
        "disable": a.disable.split(",") if a.disable else None,
        "indent_size": a.indent_size,
    }
    try:
        cfg = config.load(a.config or config.find_config(), overrides)
    except ConfigError as e:
        print(f"mdlint: config error: {e}", file=sys.stderr)
        return 2
    if a.print_config:
        print(json.dumps(cfg, ensure_ascii=False, sort_keys=True))
        return 0
    problems = runner.run(a.paths or ["."], cfg)
    print(report.render(problems, a.format))
    return 1 if problems else 0
