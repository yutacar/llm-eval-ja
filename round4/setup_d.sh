#!/usr/bin/env bash
# 第4回（OpenCode・C1〜C5）の作業フォルダを作る。  例: bash setup_d.sh ud-iq4_xs
set -euo pipefail
LABEL=${1:?ラベルを指定してください（例: ud-iq4_xs）}
HERE=$(cd "$(dirname "$0")" && pwd)
W=~/work
mkdir -p "$W"
for T in ${TASKS:-c1 c2 c3 c4 c5}; do
  DIR=$W/$T-$LABEL
  if [ -e "$DIR" ]; then echo "既にあります: $DIR（やり直すときは消してから）"; continue; fi
  cp -r "$HERE/$T/template" "$DIR"
  (cd "$DIR" && git init -q && git add -A && git -c user.name=eval -c user.email=eval@local commit -qm start)
  echo "作成: $DIR"
done
