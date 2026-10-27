#!/usr/bin/env bash
# 1つのモデルで全課題（第1回〜第3回＋繰り返し）を順に実行する
# 使い方: bash run_all.sh <ラベル> <strata-use の名前>
set -uo pipefail
LABEL=${1:?ラベル}; NAME=${2:?strata-use の名前}
cd "$(dirname "$0")"
mkdir -p logs
exec > >(tee -a "logs/$LABEL.log") 2>&1
export STRATA_BENCH_KEY="$(cat ~/.strata_key)"
sudo -v || exit 1
( while sleep 50; do sudo -n true || exit; done ) & KEEP=$!
trap 'kill $KEEP 2>/dev/null' EXIT

echo "===== $LABEL（$NAME）開始 $(date '+%F %T')"
bash -ic "strata-use $NAME" || { echo "切り替えに失敗"; exit 1; }
bash -ic "strata-bench --config strata-$NAME.json --port 8081" || echo "（ベンチは失敗。続行）"
python3 eval2.py --label "$LABEL"          # 第1回: A1 A2 A4
python3 eval3.py --label "$LABEL"          # 第3回: A3 A5 A6 A7 A8
bash repeat.sh "$LABEL"                    # A5 A6 A7 をあと2回
bash setup_b.sh "$LABEL"
bash setup_c.sh "$LABEL"
for T in b1 b3 b5 b4 b2; do bash run_b.sh "$LABEL" "$T"; done
echo "===== $LABEL 完了 $(date '+%F %T')"
