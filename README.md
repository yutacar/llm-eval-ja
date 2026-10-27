# llm-eval-ja：ローカルLLM比較用の評価セット

Strata（OpenAI 互換 API）と OpenCode で、2つのモデルに同じ問題を同じ条件で解かせて比べるためのスクリプトです。
2026-10-26〜27 に UD-IQ4_XS（Swift 1.5）と DeepSeek V4.1 Flash 2.25bpw を、2日間・3回のテストで比較しました。結果は [results.md](results.md)。

| 回 | 課題 | 方法 | 採点 |
|---|---|---|---|
| 第1回 | A1 長文読解（約2万字の資料から10問） | API | 自動（grade_a.py） |
| 第1回 | A2 日本語の文章（8題） | API | 目隠しで自分が選ぶ（blind_a2.py） |
| 第1回 | A4 JSON 抽出（20件） | API | 自動（grade_a.py） |
| 第2回 | B1 バグ修正（テスト付きの小さなライブラリ） | OpenCode | 自動（grade_b1.py、隠しテストあり） |
| 第2回 | B3 Strata v0.2.5 のコードを読んで5問 | OpenCode | 半自動（grade_b3.py） |

条件はどちらのモデルも同じ: temperature 0.6、思考の上限 2048 トークン（API）、OpenCode は 1 作業 90 分まで・手助けなし。

## 第1回（API の基本課題）

```bash
cd ~/work/llm-eval-ja
export STRATA_BENCH_KEY="$(cat ~/.strata_key)"

# UD-IQ4_XS
strata-use unsloth-ud-iq4_xs
python3 eval2.py --label ud-iq4_xs

# DeepSeek
strata-use deepseek-v4.1-flash-ist-das-2.25bpw
python3 eval2.py --label deepseek-2.25

# 採点
python3 grade_a.py -v
python3 blind_a2.py ud-iq4_xs deepseek-2.25
explorer.exe blind_a2.html
```

- 途中で止まっても、もう一度同じコマンドを実行すれば続きから再開します（済んだ問題は飛ばす）
- 1問をやり直すときは `results/<ラベル>/` の該当ファイルを消してから再実行
- 目安: UD-IQ4_XS 約15分、DeepSeek 約1時間

## 第2回（OpenCode の基本課題）

```bash
cd ~/work/llm-eval-ja

# UD-IQ4_XS
strata-use unsloth-ud-iq4_xs
bash setup_b.sh ud-iq4_xs
bash run_b.sh ud-iq4_xs b1
bash run_b.sh ud-iq4_xs b3

# DeepSeek（夜に回すのがおすすめ）
strata-use deepseek-v4.1-flash-ist-das-2.25bpw
bash setup_b.sh deepseek-2.25
bash run_b.sh deepseek-2.25 b1 ; bash run_b.sh deepseek-2.25 b3

# 採点
python3 grade_b1.py ~/work/b1-ud-iq4_xs
python3 grade_b1.py ~/work/b1-deepseek-2.25
python3 grade_b3.py ~/work/b3-ud-iq4_xs
python3 grade_b3.py ~/work/b3-deepseek-2.25
```

- 作業フォルダは `~/work/b1-<ラベル>` と `~/work/b3-<ラベル>`。ログは各フォルダの `opencode.log`、所要時間は `time.txt`
- B1 は元のテスト 22 件＋隠しテスト 5 件。tests/ を書き換えても、採点は元のテストで行います
- B3 は Strata v0.2.5 を GitHub から取得して読ませます（読むだけ。自分の ~/ai/strata-engine には触れません）
- やり直すときは作業フォルダを消して setup_b.sh から

## 第3回（難しめの課題）

第1回・第2回は両モデルとも満点だったので、差が出るように難しくした課題と、まだ測っていない力を足しました。

| 課題 | 内容 | 方法 | 採点 |
|---|---|---|---|
| A3 推論 | 答えが一つに決まる文章題・論理パズル10問を各2回 | API | 自動（正答率と、2回の結果が揃うか） |
| A5 知らないことへの対応 | 架空・誤った前提の質問6問＋実在の対照2問 | API | 半自動（-v で回答を目で確認） |
| A6 長文読解・難 | 約3万字。最後の「訂正」の反映、似た駅名、絞り込み・数え上げ | API | 自動 |
| A7 指示追従 | 字数・語の順番・形式などの条件付き10問 | API | 自動 |
| A8 ツール呼び出し | 天気・換算・電車・計算の4ツール、8問（呼ばないのが正解の問題あり） | API | 自動 |
| B2 機能追加 | 五重塔に雪景色モードを追加（元のコードは両モデルとも UD-IQ4_XS 版） | OpenCode | 自動＋見た目 |
| B4 新しいツール | 家計簿 CSV 集計コマンドを仕様から作る | OpenCode | 自動（隠しの入力12項目） |
| B5 難しいバグ修正 | 電卓言語のインタプリタ（字句解析・構文解析・評価）に6つのバグ | OpenCode | 自動（隠しテストあり） |

```bash
cd ~/work/llm-eval-ja
export STRATA_BENCH_KEY="$(cat ~/.strata_key)"

# API（A3・A5・A6・A7・A8）
strata-use unsloth-ud-iq4_xs
python3 eval3.py --label ud-iq4_xs
strata-use deepseek-v4.1-flash-ist-das-2.25bpw
python3 eval3.py --label deepseek-2.25
python3 grade_c.py -v

# OpenCode（B2・B4・B5）
strata-use unsloth-ud-iq4_xs
bash setup_c.sh ud-iq4_xs
bash run_b.sh ud-iq4_xs b5 ; bash run_b.sh ud-iq4_xs b4 ; bash run_b.sh ud-iq4_xs b2
strata-use deepseek-v4.1-flash-ist-das-2.25bpw
bash setup_c.sh deepseek-2.25
bash run_b.sh deepseek-2.25 b5 ; bash run_b.sh deepseek-2.25 b4 ; bash run_b.sh deepseek-2.25 b2

# 採点
for L in ud-iq4_xs deepseek-2.25; do
  python3 grade_b5.py ~/work/b5-$L; python3 grade_b4.py ~/work/b4-$L; node grade_b2.mjs ~/work/b2-$L
done
```

- A3 だけは思考の上限を 4096 にしています（両モデル同じ）
- A6 は入力が約2.4万トークンです。DeepSeek の設定の --max-context が 32768 以上であることを確認してください
- B2 の見た目は `~/work/b2-<ラベル>/index.html` を開き、S キーで確認します

## 追加: 繰り返し（A5・A6・A7）

1回だけの結果がたまたまかを確かめるため、A5・A6・A7 を同じ条件であと2回ずつ実行する（1回目は第3回の結果を使う）。

```bash
strata-use unsloth-ud-iq4_xs && bash repeat.sh ud-iq4_xs
strata-use deepseek-v4.1-flash-ist-das-2.25bpw && bash repeat.sh deepseek-2.25
python3 grade_repeat.py ud-iq4_xs deepseek-2.25
```

## B2 の元コード

`b2/base/` は、事前テストで UD-IQ4_XS が OpenCode で作った五重塔（`pagoda-gen.js`、`index.html`、`check.mjs`）です。両モデルともここから雪景色を追加させました。

## 注意

- 隠しテスト（`*/hidden/`）や B3 の答え（`grade_b3.py`）、B4 の正解（`grade_b4.py`）も含めて公開しています。評価するモデルには作業フォルダの外を読ませないでください
- A5 の自動判定は言い回しで判定する目安です。最終的には `grade_c.py -v` で回答を目で確認しています
- A2（日本語の文章）の判定は人が行う前提です。results.md の A2 は Claude がモデル名を伏せて判定した結果です

## 新しいモデルを足して比べる

Strata でモデルを入れたら、`run_all.sh` で全課題を順に実行できます（最初に sudo のパスワードを1回入力）。

```bash
bash run_all.sh <ラベル> <strata-use の名前>     # 例: bash run_all.sh qwen36-q4 qwen36-ud-q4_k_xl
python3 grade_repeat.py ud-iq4_xs <ラベル>        # 繰り返しの採点を並べる
```

OpenCode の課題の採点は `grade_b1.py`〜`grade_b5.py` と `grade_b2.mjs` に作業フォルダ（`~/work/b?-<ラベル>`）を渡します。
