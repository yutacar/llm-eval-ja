#!/usr/bin/env bash
# 第4回を全部まとめて実行する: モデルを切り替えながら C1〜C5 を OpenCode で解かせ、最後に採点する。
#   bash run_all_d.sh                    # 4モデル × 5課題
#   MODELS="ud-iq4_xs=unsloth-ud-iq4_xs" TASKS="c1 c2" bash run_all_d.sh   # 絞って実行
# 途中で止めても、もう一度実行すれば終わった課題（time.txt があるもの）は飛ばして続きから。
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
MODELS=${MODELS:-"ud-iq4_xs=unsloth-ud-iq4_xs qwen36=qwen36-ud-q4_k_xl coder=coder-iq1_m deepseek-2.25=deepseek-v4.1-flash-ist-das-2.25bpw"}
export TASKS=${TASKS:-"c1 c2 c3 c4 c5"}
mkdir -p "$HERE/logs"

command -v opencode >/dev/null || { echo "opencode が見つかりません（PATH を確認）"; exit 1; }
# ~/.bashrc の関数（strata-use など）をこのスクリプトの中に読み込む
shopt -s extglob
eval "$(bash -ic 'declare -f $(compgen -A function strata)' </dev/null 2>/dev/null)"
type strata-use >/dev/null 2>&1 || { echo "strata-use が見つかりません（~/.bashrc を確認）"; exit 1; }
echo "sudo のパスワード（モデルの切り替えに使います）"
sudo -v || exit 1
( while true; do sudo -n true; sleep 60; done ) 2>/dev/null &
KEEP=$!
trap 'kill $KEEP 2>/dev/null' EXIT
sudo systemctl stop comfyui 2>/dev/null

for pair in $MODELS; do
  LABEL=${pair%%=*}; RUN=${pair#*=}
  LOG="$HERE/logs/d-$LABEL.log"
  todo=""
  for T in $TASKS; do [ -f ~/work/$T-$LABEL/time.txt ] || todo="$todo $T"; done
  if [ -z "$todo" ]; then echo "== $LABEL: 全部終わっています"; continue; fi
  echo "== $LABEL（$RUN）: $todo  $(date '+%F %T')" | tee -a "$LOG"
  strata-use "$RUN" </dev/null >>"$LOG" 2>&1 || { echo "   モデルの切り替えに失敗: $RUN（$LOG を見てください）"; continue; }
  bash "$HERE/setup_d.sh" "$LABEL" >>"$LOG" 2>&1
  for T in $todo; do
    echo "   $T 開始 $(date '+%T')"
    bash "$HERE/run_d.sh" "$LABEL" "$T" >>"$LOG" 2>&1
    echo "   $T 終了 $(date '+%T')  $(tail -c 120 ~/work/$T-$LABEL/time.txt | grep -o '所要.*')"
  done
done

echo "== 採点 $(date '+%F %T')"
python3 "$HERE/grade_d.py" | tee "$HERE/results-d.txt"
echo "結果: $HERE/results-d.txt（詳しくは python3 grade_d.py -v）"
