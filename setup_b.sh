#!/usr/bin/env bash
# 2日目の作業フォルダを作る。  例: bash setup_b.sh ud-iq4_xs
set -euo pipefail
LABEL=${1:?ラベルを指定してください（例: ud-iq4_xs）}
HERE=$(cd "$(dirname "$0")" && pwd)
W=~/work

# B1: バグ入りプロジェクト（git で変更を追えるようにする）
B1=$W/b1-$LABEL
if [ -e "$B1" ]; then echo "既にあります: $B1（やり直すときは消してから）"; else
  cp -r "$HERE/b1/template" "$B1"
  (cd "$B1" && git init -q && git add -A && git -c user.name=eval -c user.email=eval@local commit -qm start)
  echo "作成: $B1"
fi

# B3: Strata v0.2.5 のソース（読むだけ）
SRC=$W/b3-src
if [ ! -d "$SRC/.git" ]; then
  git clone -q --depth 1 --branch v0.2.5 https://github.com/Niko1221/Strata "$SRC"
fi
B3=$W/b3-$LABEL
if [ -e "$B3" ]; then echo "既にあります: $B3（やり直すときは消してから）"; else
  git clone -q "$SRC" "$B3"
  echo "作成: $B3（$(cd "$B3" && git describe --tags 2>/dev/null || git log -1 --format=%h)）"
fi
