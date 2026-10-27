#!/usr/bin/env bash
# 第3回（OpenCode）の作業フォルダを作る。  例: bash setup_c.sh ud-iq4_xs
# B2 の元にする五重塔は、既定でリポジトリの b2/base（PAGODA_SRC=... で変更可）
set -euo pipefail
LABEL=${1:?ラベルを指定してください（例: ud-iq4_xs）}
HERE=$(cd "$(dirname "$0")" && pwd)
W=~/work
PAGODA_SRC=${PAGODA_SRC:-$HERE/b2/base}   # リポジトリ同梱の元コード（自分の五重塔を使うときは PAGODA_SRC=... で指定）
init_git() { (cd "$1" && git init -q && git add -A && git -c user.name=eval -c user.email=eval@local commit -qm start --allow-empty); }

# B2: 五重塔に雪景色を追加（両モデルとも同じ元のコードから）
if [ ! -d "$W/b2-src" ]; then
  for f in pagoda-gen.js index.html check.mjs; do
    [ -f "$PAGODA_SRC/$f" ] || { echo "見つかりません: $PAGODA_SRC/$f（PAGODA_SRC で指定してください）"; exit 1; }
  done
  mkdir -p "$W/b2-src" && cp "$PAGODA_SRC"/{pagoda-gen.js,index.html,check.mjs} "$W/b2-src/"
  echo "元のコード: $W/b2-src（$PAGODA_SRC から）"
fi
for T in b2 b4 b5; do
  DIR=$W/$T-$LABEL
  if [ -e "$DIR" ]; then echo "既にあります: $DIR（やり直すときは消してから）"; continue; fi
  case $T in
    b2) mkdir -p "$DIR" && cp "$W/b2-src"/* "$DIR/" ;;
    b4) mkdir -p "$DIR" ;;
    b5) cp -r "$HERE/b5/template" "$DIR" ;;
  esac
  init_git "$DIR"
  echo "作成: $DIR"
done
