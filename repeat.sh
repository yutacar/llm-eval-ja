#!/usr/bin/env bash
# A5・A6・A7 を追加で繰り返す（1回目は第3回の結果をそのまま使う）。
# 例: bash repeat.sh ud-iq4_xs          → ud-iq4_xs-r2, ud-iq4_xs-r3 を作る
#     bash repeat.sh deepseek-2.25 4    → r2〜r4 の3回分
set -euo pipefail
LABEL=${1:?ラベル（例: ud-iq4_xs）}; LAST=${2:-3}
cd "$(dirname "$0")"
export STRATA_BENCH_KEY="${STRATA_BENCH_KEY:-$(cat ~/.strata_key 2>/dev/null || true)}"
for i in $(seq 2 "$LAST"); do
  echo "=== $LABEL-r$i ==="
  python3 eval3.py --label "$LABEL-r$i" --tasks a5,a6,a7
done
