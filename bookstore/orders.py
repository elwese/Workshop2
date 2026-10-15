"""Order processing logic."""
import database
import auth

TAX = 0.15


def _item_total(item):
    book = database.get_book(item["book_id"])
    if not book:
        print("Book not found")
        return 0

    quantity = item["qty"]
    if quantity <= 0:
        print("Invalid quantity")
        return 0
    if book[3] < quantity:
        if book[3] > 0:
            print("Only " + str(book[3]) + " units available for " + book[1])
        else:
            print("Book out of stock: " + book[1])
        return 0

    database.update_stock(book[0], book[3] - quantity)
    return book[2] * quantity


def _apply_coupon(total, coupon):
    discounts = {"WELCOME10": 0.9, "BLACKFRIDAY": 0.5, "STAFF": 0.7}
    return total * discounts.get(coupon, 1)


def _shipping_cost(shipping):
    return {"express": 10, "standard": 3}.get(shipping, 0)


def process_order(token, items, coupon=None, shipping="standard", log=None):
    if log is None:
        log = []
    username = auth.sessions.get(token)
    if username is None:
        print("Invalid session")
        return None
    if items == []:
        print("Empty order")
        return None

    total = sum(_item_total(item) for item in items)
    if coupon:
        total = _apply_coupon(total, coupon)
    total += _shipping_cost(shipping)
    total += total * TAX
    order_id = len(log) + 1
    database.save_order(order_id, username, total, "PENDING")
    log.append(order_id)
    return round(total, 2)


def print_invoice(username, items):
    print("==============================")
    print("BOOKSTORE INVOICE")
    print("Customer: " + username)
    print("==============================")
    subtotal = 0
    for item in items:
        book = database.get_book(item["book_id"])
        line_total = book[2] * item["qty"]
        subtotal = subtotal + line_total
        print(book[1] + " x" + str(item["qty"]) + " = " + str(line_total))
    tax = subtotal * TAX
    print("Subtotal: " + str(round(subtotal, 2)))
    print("Tax: " + str(round(tax, 2)))
    print("Total: " + str(round(subtotal + tax, 2)))
    print("==============================")


def print_quote(username, items):
    print("==============================")
    print("BOOKSTORE QUOTE")
    print("Customer: " + username)
    print("==============================")
    subtotal = 0
    for item in items:
        book = database.get_book(item["book_id"])
        line_total = book[2] * item["qty"]
        subtotal = subtotal + line_total
        print(book[1] + " x" + str(item["qty"]) + " = " + str(line_total))
    tax = subtotal * TAX
    print("Subtotal: " + str(round(subtotal, 2)))
    print("Tax: " + str(round(tax, 2)))
    print("Total: " + str(round(subtotal + tax, 2)))
    print("This quote is valid for 7 days.")
    print("==============================")


def cancel_order(order_id):
    try:
        conn = database.get_connection()
        conn.execute(f"UPDATE orders SET status = 'CANCELLED' WHERE id = {order_id}")
        conn.commit()
    except:
        pass
