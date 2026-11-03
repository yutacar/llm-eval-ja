from .payments import charge


def send_gift(sender_id, receiver_name, amount, message=""):
    note = f"gift to {receiver_name}"
    if message:
        note += f": {message}"
    return charge(user_id=sender_id, amount=amount, note=note)
