import dataclasses
import unittest

from shop import ledger, points
from shop.payments import charge, Payment
from shop.cart import Cart
from shop.coupon import pay_with_coupon
from shop.subscription import renew, renewer
from shop.gift import send_gift
from shop.shipping import charge_shipping
from shop.invoice import bill_all
from shop.marketplace import buy_from_seller
from shop.donation import round_up_donation
from shop import cli, reports


class HiddenTest(unittest.TestCase):
    def setUp(self):
        ledger.reset()
        points.reset()

    def test_payment_defaults(self):
        p = Payment(1, 500)
        self.assertEqual((p.user_id, p.amount, p.currency, p.note), (1, 500, "JPY", None))

    def test_payment_is_frozen(self):
        p = Payment(1, 500)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            p.amount = 1

    def test_payment_validation(self):
        for args in [(0, 100), (1, 0), (1, -5), (1, 100, "GBP"), ("1", 100), (1, 1.5)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                Payment(*args)

    def test_charge_new_api(self):
        r = charge(Payment(1, 500, "USD", "x"))
        self.assertEqual((r["user_id"], r["amount"], r["currency"], r["note"]), (1, 500, "USD", "x"))
        self.assertEqual(ledger.entries()[-1]["amount"], 500)

    def test_old_api_rejected(self):
        with self.assertRaises(TypeError):
            charge(1, 500)
        with self.assertRaises(TypeError):
            charge({"user_id": 1, "amount": 500})

    def test_cart(self):
        c = Cart(2)
        c.add("pen", 120, 3)
        c.add("note", 300)
        r = c.checkout()
        self.assertEqual((r["amount"], r["note"]), (660, "cart:2 items"))

    def test_coupon(self):
        r = pay_with_coupon(3, 999, 0.1)
        self.assertEqual((r["amount"], r["currency"], r["note"]), (899, "JPY", "coupon"))

    def test_subscription(self):
        r = renew(4, "basic")
        self.assertEqual((r["user_id"], r["amount"], r["note"]), (4, 980, "subscription"))
        self.assertEqual(renewer(5)(2980)["user_id"], 5)

    def test_gift(self):
        r = send_gift(5, "Mei", 2000)
        self.assertEqual((r["user_id"], r["amount"], r["note"]), (5, 2000, "gift to Mei"))

    def test_shipping(self):
        r = charge_shipping(6, "DE")
        self.assertEqual((r["amount"], r["currency"], r["note"]), (20, "EUR", "shipping:DE"))

    def test_invoice(self):
        rs = bill_all([{"user_id": 7, "amount": 100}, {"user_id": 8, "amount": 5, "currency": "USD"}])
        self.assertEqual([(r["user_id"], r["amount"], r["currency"], r["note"]) for r in rs],
                         [(7, 100, "JPY", "invoice"), (8, 5, "USD", "invoice")])

    def test_points(self):
        points.add_points(9, 1500)
        self.assertIsNone(points.pay_with_points(9, 1000))
        r = points.pay_with_points(9, 800)
        self.assertEqual((r["amount"], r["note"]), (300, "points used:500"))

    def test_marketplace(self):
        rs = buy_from_seller(10, 11, 5)
        self.assertEqual([(r["user_id"], r["amount"], r["note"]) for r in rs], [(10, 5, "purchase")])

    def test_donation(self):
        self.assertIsNone(round_up_donation(12, 1200))
        r = round_up_donation(12, 1201)
        self.assertEqual((r["amount"], r["note"]), (99, "donation"))

    def test_cli(self):
        self.assertEqual(cli.main(["13", "250"]), 0)
        e = ledger.entries()[-1]
        self.assertEqual((e["user_id"], e["amount"], e["currency"], e["note"]), (13, 250, "JPY", "manual"))

    def test_reports(self):
        charge(Payment(1, 100))
        charge(Payment(2, 7, "USD"))
        charge(Payment(3, 50))
        self.assertEqual(reports.total_by_currency(), {"JPY": 150, "USD": 7})


if __name__ == "__main__":
    unittest.main()
