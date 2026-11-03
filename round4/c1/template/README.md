# shop

小さなネットショップの決済まわり。どの機能も最後は `shop/payments.py` の `charge()` を呼びます。

- テスト: `python3 -m unittest -v`
- 手動請求: `python3 -m shop.cli USER_ID AMOUNT [CURRENCY]`
