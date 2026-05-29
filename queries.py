GET_USER_ROLE = """
SELECT role
FROM users
WHERE login = %s AND password = %s;
"""

CHECK_LOGIN_EXISTS = """
SELECT login
FROM users
WHERE login = %s;
"""

INSERT_USER = """
INSERT INTO users (
    login,
    password,
    phone_num,
    address,
    role,
    favorite_category
)
VALUES (%s, %s, %s, %s, %s, %s);
"""


INSERT_ITEM = """
INSERT INTO item (
    item_name,
    category,
    starting_price,
    image_url,
    item_condition,
    description,
    seller_login
)
VALUES (%s, %s, %s, %s, %s, %s, %s)
RETURNING item_id;
"""


INSERT_AUCTION = """
INSERT INTO auction (
    item_id,
    seller_login
)
VALUES (%s, %s)
RETURNING auction_id;
"""


INSERT_BID = """
INSERT INTO bid (
    auction_id,
    buyer_login,
    bid_amount
)
VALUES (%s, %s, %s)
RETURNING bid_id;
"""


INSERT_PAYMENT = """
INSERT INTO payment (
    auction_id,
    buyer_login,
    amount
)
VALUES (%s, %s, %s)
RETURNING payment_id;
"""


INSERT_SHIPMENT = """
INSERT INTO shipment (
    auction_id,
    address
)
VALUES (%s, %s)
RETURNING shipment_id;
"""

GET_USER_INFO = """
SELECT phone_num, address, favorite_category
FROM users
WHERE login = %s;
"""

# Used to allow users to see/edit their profile.
GET_USER_INFO = """
SELECT phone_num, address, favorite_category, password
FROM users
WHERE login = %s;
"""

UPDATE_USER_INFO = """
UPDATE users
SET phone_num = %s,
    address = %s,
    favorite_category = %s,
    password = %s
WHERE login = %s;
"""