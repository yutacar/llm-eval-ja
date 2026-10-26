# llm-eval2：UD-IQ4_XS と DeepSeek の追加比較

| 日 | 課題 | 方法 | 採点 |
|---|---|---|---|
| 1日目 | A1 長文読解（約2万字の資料から10問） | API | 自動（grade_a.py） |
| 1日目 | A2 日本語の文章（8題） | API | 目隠しで自分が選ぶ（blind_a2.py） |
| 1日目 | A4 JSON 抽出（20件） | API | 自動（grade_a.py） |
| 2日目 | B1 バグ修正（テスト付きの小さなライブラリ） | OpenCode | 自動（grade_b1.py、隠しテストあり） |
| 2日目 | B3 Strata v0.2.5 のコードを読んで5問 | OpenCode | 半自動（grade_b3.py） |

条件はどちらのモデルも同じ: temperature 0.6、思考の上限 2048 トークン（API）、OpenCode は 1 作業 90 分まで・手助けなし。

## 1日目（API）

```bash
cd ~/work/llm-eval2
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

## 2日目（OpenCode）

```bash
cd ~/work/llm-eval2

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
