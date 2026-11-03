"""python3 -m shop.cli <user_id> <amount> [currency] で手動請求する。"""
import sys

from .payments import charge


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) < 2:
        print("usage: shop.cli USER_ID AMOUNT [CURRENCY]")
        return 2
    user_id, amount = int(args[0]), int(args[1])
    currency = args[2] if len(args) > 2 else "JPY"
    r = charge(user_id, amount, currency, note="manual")
    print(f"charged #{r['id']}: {r['amount']} {r['currency']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
