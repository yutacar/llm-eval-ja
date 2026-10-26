#!/usr/bin/env bash
# OpenCode で B1 / B3 を実行する（上限 90 分）。  例: bash run_b.sh ud-iq4_xs b1
set -uo pipefail
LABEL=${1:?ラベル}; TASK=${2:?b1 か b3}
HERE=$(cd "$(dirname "$0")" && pwd)
DIR=~/work/$TASK-$LABEL
[ -d "$DIR" ] || { echo "先に bash setup_b.sh $LABEL を実行してください"; exit 1; }
cd "$DIR"
START=$(date +%s)
echo "開始: $(date '+%F %T')  $DIR"
timeout 90m opencode run -m strata/swift-1.5-iq2_xs "$(cat "$HERE/$TASK/prompt.txt")" 2>&1 | tee opencode.log
RC=${PIPESTATUS[0]}
MIN=$(( ($(date +%s) - START + 30) / 60 ))
echo "終了: $(date '+%F %T')  所要 ${MIN} 分  終了コード ${RC}（124 = 90分で打ち切り）" | tee time.txt
