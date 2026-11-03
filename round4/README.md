# 第4回: OpenCode の評価（C1〜C5）

前回までの B1〜B5 は1つのファイルの中で終わる作業が中心だったので、それを補う5つの課題です。どれも Python の標準ライブラリだけで動き、隠しテストで自動採点します。

| 課題 | 内容 | 主に測る力 | 隠しテスト |
|---|---|---|---|
| C1 複数ファイルにまたがる仕様変更 | 決済ライブラリ（約15ファイル）の `charge(user_id, amount, ...)` を `charge(Payment)` に変え、呼んでいる箇所（位置引数・キーワード・`**kw`・`functools.partial`・別名で呼ぶものなど11か所）とテストを全部直す | 影響する箇所を漏れなく探す力。同じ書き換えを正確に繰り返す力 | 21 |
| C2 失敗ログからの原因調査 | 予約システムで、手元では通るのに CI（UTC）だけ落ちる。原因はタイムゾーンの扱いで、同じ原因の箇所がほかに2つある | ログを読む・再現する・根本を直す力（見えている失敗だけ直すと隠しテストで落ちる） | 24（UTC と LA で各12） |
| C3 日本語のデータ処理 | 和暦⇔西暦（元号の境目）、全角半角の正規化（NFKC 丸投げは不可）、住所の分割（四日市市・大和郡山市・政令市の区など）、郵便番号を仕様書から作る | 日本特有の知識の正確さ | 90 |
| C4 セキュリティの修正 | メモアプリ（WSGI）に、場所を伏せた穴が4つ（検索の SQL インジェクション、トークンの SQL インジェクション、パストラバーサル、cookie を信じる管理者判定）。攻撃テストも自分で書かせる | 危険な書き方を見つけて、普通の機能を壊さずに直す力 | 20 |
| C5 大きめのリポジトリで設定を1つ追加 | Markdown の検査ツール（約50ファイル）に設定項目 `max_line_length` を追加し、読み込み・検証・引数・`--print-config`・`--help`・ドキュメントまで通す | 知らないコードの中を探して、既存の作りにそろえる力 | 16 |

条件は前回と同じ: OpenCode に課題文（`cN/prompt.txt`）を1回渡すだけ、手助けなし、1課題90分まで。

## 一括実行

```bash
cd ~/work/llm-eval-d
bash run_all_d.sh
```

- 4つのモデル（UD-IQ4_XS → Qwen3.6 → Coder → DeepSeek の順）を `strata-use` で切り替えながら、C1〜C5 を順に解かせ、最後に採点して `results-d.txt` に保存します
- 途中で止まっても（Ctrl+C、PC の再起動など）、もう一度同じコマンドを実行すれば、終わった課題（`time.txt` があるもの）は飛ばして続きから始まります
- 進み具合: 別のターミナルで `tail -f ~/work/llm-eval-d/logs/d-<ラベル>.log`
- 目安: UD・Qwen3.6・Coder は各30分〜1時間半、DeepSeek は3〜7時間（全部で6〜10時間）。夜に回すのがおすすめ

絞って実行する例:

```bash
MODELS="ud-iq4_xs=unsloth-ud-iq4_xs" bash run_all_d.sh                 # 1モデルだけ
TASKS="c2 c4" bash run_all_d.sh                                         # 課題を絞る
MODELS="deepseek-2.25=deepseek-v4.1-flash-ist-das-2.25bpw" LIMIT=120m bash run_all_d.sh   # 上限を120分に
```

`MODELS` は `ラベル=strata-use に渡す名前` を空白で区切って並べます。名前は `ls ~/ai/strata-engine/run-*.sh` の `run-` と `.sh` の間です。

## 採点だけ

```bash
python3 grade_d.py            # 表
python3 grade_d.py -v         # 落ちたテストの名前、変えたファイルも
python3 grade_d.py qwen36     # ラベルを指定
```

- 採点は作業フォルダのコピーで行います（作業フォルダは変えません）
- 変えてはいけないファイル（C2〜C5 の元のテストなど）は元に戻してから検査し、書き換えられていたら「改変」と表示します
- 1課題だけやり直すときは `rm -rf ~/work/c3-<ラベル>` してから `bash run_all_d.sh`

## ファイル

```
run_all_d.sh   一括実行（モデル切り替え → 作業フォルダ作成 → 実行 → 採点）
setup_d.sh     作業フォルダ ~/work/cN-<ラベル> を作る（git で最初の状態を記録）
run_d.sh       課題を1つ OpenCode で実行（LIMIT=90m、OC_MODEL で OpenCode のモデル名を変更可）
grade_d.py     採点
tools/count_tests.py   subTest も1件ずつ数える unittest の実行役
cN/template/   課題の元のコード
cN/prompt.txt  OpenCode に渡す課題文
cN/hidden/     隠しテスト（作業フォルダには入れない）
```
