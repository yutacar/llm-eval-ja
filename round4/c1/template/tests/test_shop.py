import unittest

from shop import ledger, points
from shop.payments import charge
from shop.cart import Cart
from shop.coupon import pay_with_coupon
from shop.subscription import renew
from shop.gift import send_gift
from shop.shipping import charge_shipping
from shop.invoice import bill_all
from shop.marketplace import buy_from_seller
from shop.donation import round_up_donation
from shop import cli


class ShopTest(unittest.TestCase):
    def setUp(self):
        ledger.reset()
        points.reset()

    def test_charge(self):
        r = charge(1, 500)
        self.assertEqual((r["user_id"], r["amount"], r["currency"]), (1, 500, "JPY"))

    def test_charge_rejects_bad_amount(self):
        with self.assertRaises(ValueError):
            charge(1, 0)

    def test_cart(self):
        c = Cart(2)
        c.add("pen", 120, 3)
        self.assertEqual(c.checkout()["amount"], 360)

    def test_coupon(self):
        self.assertEqual(pay_with_coupon(3, 1000, 0.15)["amount"], 850)

    def test_subscription(self):
        self.assertEqual(renew(4, "pro")["amount"], 2980)

    def test_gift(self):
        self.assertEqual(send_gift(5, "Aki", 3000, "おめでとう")["note"], "gift to Aki: おめでとう")

    def test_shipping(self):
        self.assertEqual(charge_shipping(6, "US")["currency"], "USD")

    def test_invoice(self):
        rs = bill_all([{"user_id": 7, "amount": 100}, {"user_id": 8, "amount": 5, "currency": "EUR"}])
        self.assertEqual([r["currency"] for r in rs], ["JPY", "EUR"])

    def test_points(self):
        points.add_points(9, 300)
        self.assertEqual(points.pay_with_points(9, 1000)["amount"], 700)

    def test_marketplace(self):
        rs = buy_from_seller(10, 11, 5000)
        self.assertEqual([(r["user_id"], r["amount"]) for r in rs], [(10, 5000), (11, 500)])

    def test_donation(self):
        self.assertEqual(round_up_donation(12, 1234)["amount"], 66)

    def test_cli(self):
        self.assertEqual(cli.main(["13", "250", "USD"]), 0)
        self.assertEqual(ledger.entries()[-1]["currency"], "USD")


if __name__ == "__main__":
    unittest.main()
