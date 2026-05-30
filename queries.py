# For seller to find their current auctions
GET_CURRENT_AUCTIONS = """
SELECT 
    a.auction_id,
    i.item_name
FROM auction a
JOIN item i ON i.item_id = a.item_id
WHERE i.seller_login = %s
  AND a.auction_status = 'Active';
"""

# When seller chooses to end auction.

FIND_AUCTION_WINNER = """
SELECT buyer_login, bid_amount
FROM bid
WHERE auction_id = %s
  AND bid_amount = (
      SELECT MAX(bid_amount)
      FROM bid
      WHERE auction_id = %s
  );
"""

CLOSE_AUCTION_ID = """
UPDATE auction
SET auction_status = 'Closed', winner_login=%s  
WHERE auction_id = %s;
"""

# Create payment for winner of auction, use default values
INSERT_PAYMENT = """
INSERT INTO payment (
    auction_id,
    buyer_login,
    amount
)
VALUES (%s, %s, %s);
"""

# For printing out item information
GET_ITEM_INFO = """
SELECT *
FROM item
WHERE item_id = %s;
"""

# For browsing items in auction
AUCTION_SEARCH_BY_NAME = """
SELECT 
    a.auction_id,
    i.item_name,
    i.category,
    i.description,
    a.current_highest_bid
FROM auction a
JOIN item i ON i.item_id = a.item_id
WHERE i.item_name LIKE %s
LIMIT 4;
"""

AUCTION_SEARCH_BY_CATEGORY = """
SELECT 
    a.auction_id,
    i.item_name,
    i.category,
    i.description,
    a.current_highest_bid
FROM auction a
JOIN item i ON i.item_id = a.item_id
WHERE i.category = %s
LIMIT 4;
"""

# For buyers to view payments
GET_PENDING_PAYMENTS = """
SELECT p.payment_id, p.auction_id, i.item_name
FROM payment p
JOIN auction a ON a.auction_id = p.auction_id
JOIN item i ON i.item_id = a.item_id
WHERE p.payment_status = 'Pending' AND buyer_login = %s;
"""

# For buyer to finish payment
SET_PAYMENT_STATUS_COMPLETED = """
UPDATE payment
SET payment_status = 'Completed'
WHERE payment_id = %s;
"""






"""
Work on everything above
"""




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
"""

UPDATE_ITEM = """

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