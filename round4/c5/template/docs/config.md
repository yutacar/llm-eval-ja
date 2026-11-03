# 設定

設定は、検査するフォルダ（かその上の階層）にある `.mdlint.toml` に書きます。コマンドラインの引数があれば、そちらが優先されます。

| 項目 | 型 | 既定値 | 引数 | 説明 |
|---|---|---|---|---|
| `disable` | 文字列の配列 | `[]` | `--disable` | 使わない規則（例: `["MD013", "MD041"]`） |
| `heading_style` | 文字列 | `"atx"` | なし | 見出しの書き方（`atx` か `setext`）。MD003 で使う |
| `indent_size` | 整数（1〜8） | `2` | `--indent-size` | リストの字下げの幅。MD007 で使う |
| `allow_trailing_spaces` | 真偽値 | `false` | なし | `true` なら行末の空白を許す（MD009） |

例:

```toml
disable = ["MD033"]
indent_size = 4
```

正しくない値を書くと、`mdlint: config error: ...` と表示して終了コード 2 で終わります。使われる設定は `mdlint --print-config` で確かめられます。
