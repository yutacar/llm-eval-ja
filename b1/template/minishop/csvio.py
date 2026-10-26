"""注文 CSV の読み込み。列: date,name,price,qty,category"""
import csv
import io

from .dates import parse_jp_date


def read_orders(text):
    rows = []
    for r in csv.DictReader(io.StringIO(text)):
        rows.append({"date": parse_jp_date(r["date"]), "name": r["name"], "price": int(r["price"]),
                     "qty": int(r["qty"]), "category": r.get("category") or "general"})
    return rows
