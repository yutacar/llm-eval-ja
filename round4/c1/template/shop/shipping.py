from .payments import charge

RATES = {"JP": (800, "JPY"), "US": (25, "USD"), "DE": (20, "EUR")}


def charge_shipping(user_id, country):
    fee, cur = RATES[country]
    return charge(user_id, fee, cur, note=f"shipping:{country}")
