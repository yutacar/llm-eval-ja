# mdlint

Markdown の書き方を検査する小さなツール（Python の標準ライブラリだけで動く）。

```
python3 -m mdlint docs/          # フォルダの中の .md を検査
python3 -m mdlint --print-config # 使われる設定を表示
python3 -m unittest -v           # テスト
```

設定は [docs/config.md](docs/config.md)、規則は [docs/rules.md](docs/rules.md) を見てください。
