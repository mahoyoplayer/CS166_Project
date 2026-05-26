import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(166)

BASE_DIR = Path(__file__).resolve().parent
OUT = BASE_DIR / "fake_data_1000.sql"

categories = ["Electronics", "Books", "Clothing", "Sports", "Home", "Toys", "Art", "Games"]
conditions = ["New", "Like New", "Good", "Fair", "Used"]
payment_statuses = ["Pending", "Completed", "Failed"]
shipment_statuses = ["Pending", "Shipped", "Delivered"]

def esc(s):
    return str(s).replace("'", "''")

def money(x):
    return f"{x:.2f}"

buyers = [f"buyer{i}" for i in range(1, 401)]
sellers = [f"seller{i}" for i in range(1, 101)]
admins = [f"admin{i}" for i in range(1, 6)]

lines = []
lines.append("-- Fake data generated for auction project")
lines.append("BEGIN;")
lines.append("")
lines.append("TRUNCATE shipment, payment, bid, auction, item, users CASCADE;")
lines.append("")

# Users
for login in buyers:
    fav = random.choice(categories)
    lines.append(
        f"INSERT INTO users VALUES "
        f"('{login}', 'password123', '555-{random.randint(1000,9999)}', "
        f"'Buyer Address {esc(login)}', 'Buyer', '{fav}');"
    )

for login in sellers:
    fav = random.choice(categories)
    lines.append(
        f"INSERT INTO users VALUES "
        f"('{login}', 'password123', '555-{random.randint(1000,9999)}', "
        f"'Seller Address {esc(login)}', 'Seller', '{fav}');"
    )

for login in admins:
    lines.append(
        f"INSERT INTO users VALUES "
        f"('{login}', 'adminpass', '555-{random.randint(1000,9999)}', "
        f"'Admin Office {esc(login)}', 'Admin', NULL);"
    )

lines.append("")

# 1000 items + 1000 auctions
auction_winners = {}
auction_prices = {}

for i in range(1, 1001):
    seller = random.choice(sellers)
    category = random.choice(categories)
    start_price = random.uniform(5, 500)
    item_name = f"{category} Item {i}"
    image_url = f"https://example.com/images/item_{i}.jpg"
    condition = random.choice(conditions)
    description = f"Fake test item {i} in {category} category."

    lines.append(
        "INSERT INTO item "
        "(item_id, item_name, category, starting_price, image_url, item_condition, description, seller_login, seller_role) "
        f"VALUES ({i}, '{esc(item_name)}', '{category}', {money(start_price)}, "
        f"'{image_url}', '{condition}', '{esc(description)}', '{seller}', 'Seller');"
    )

    is_closed = i % 3 == 0
    winner = random.choice(buyers) if is_closed else None
    final_price = start_price + random.uniform(10, 300) if is_closed else 0
    auction_winners[i] = winner
    auction_prices[i] = final_price if is_closed else start_price

    winner_sql = f"'{winner}'" if winner else "NULL"
    winner_role_sql = "'Buyer'" if winner else "NULL"
    status = "Closed" if is_closed else "Active"

    lines.append(
        "INSERT INTO auction "
        "(auction_id, item_id, seller_login, seller_role, current_highest_bid, auction_status, winner_login, winner_role) "
        f"VALUES ({i}, {i}, '{seller}', 'Seller', {money(final_price)}, "
        f"'{status}', {winner_sql}, {winner_role_sql});"
    )

lines.append("")

# 1000 bids
for bid_id in range(1, 1001):
    auction_id = random.randint(1, 1000)
    buyer = auction_winners.get(auction_id) or random.choice(buyers)
    amount = max(1, auction_prices[auction_id] + random.uniform(1, 100))
    ts = datetime.now() - timedelta(days=random.randint(0, 90), minutes=random.randint(0, 1440))

    lines.append(
        "INSERT INTO bid "
        "(bid_id, auction_id, buyer_login, buyer_role, bid_amount, bid_timestamp) "
        f"VALUES ({bid_id}, {auction_id}, '{buyer}', 'Buyer', {money(amount)}, "
        f"'{ts.strftime('%Y-%m-%d %H:%M:%S')}');"
    )

lines.append("")

# Payments and shipments only for closed auctions
payment_id = 1
shipment_id = 1
for auction_id, winner in auction_winners.items():
    if winner is None:
        continue

    amount = auction_prices[auction_id]
    pay_status = random.choice(payment_statuses)
    ship_status = random.choice(shipment_statuses)
    tracking = f"TRACK{auction_id:06d}" if ship_status != "Pending" else None
    tracking_sql = f"'{tracking}'" if tracking else "NULL"

    lines.append(
        "INSERT INTO payment "
        "(payment_id, auction_id, buyer_login, buyer_role, amount, payment_status) "
        f"VALUES ({payment_id}, {auction_id}, '{winner}', 'Buyer', {money(amount)}, '{pay_status}');"
    )

    lines.append(
        "INSERT INTO shipment "
        "(shipment_id, auction_id, address, shipment_status, tracking_number) "
        f"VALUES ({shipment_id}, {auction_id}, 'Shipping Address for {winner}', "
        f"'{ship_status}', {tracking_sql});"
    )

    payment_id += 1
    shipment_id += 1

lines.append("")
lines.append("COMMIT;")

OUT.write_text("\n".join(lines))
print(f"Wrote {OUT}")
