#!/usr/bin/env bash
# OpenCode で課題を1つ実行する（上限 90 分）。  例: bash run_d.sh ud-iq4_xs c1
set -uo pipefail
LABEL=${1:?ラベル}; TASK=${2:?c1〜c5}
HERE=$(cd "$(dirname "$0")" && pwd)
DIR=~/work/$TASK-$LABEL
LIMIT=${LIMIT:-90m}
MODEL=${OC_MODEL:-strata/swift-1.5-iq2_xs}   # OpenCode の設定にある Strata のモデル名（中身は今 Strata で動いているモデル）
[ -d "$DIR" ] || { echo "先に bash setup_d.sh $LABEL を実行してください"; exit 1; }
cd "$DIR"
START=$(date +%s)
echo "開始: $(date '+%F %T')  $DIR"
timeout "$LIMIT" opencode run -m "$MODEL" "$(cat "$HERE/$TASK/prompt.txt")" 2>&1 | tee opencode.log
RC=${PIPESTATUS[0]}
SEC=$(( $(date +%s) - START ))
echo "終了: $(date '+%F %T')  所要 $(( (SEC + 30) / 60 )) 分（${SEC} 秒）  終了コード ${RC}（124 = 時間切れ）" | tee time.txt
