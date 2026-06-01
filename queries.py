# Query for buyers to see their shipped shipments to mark as delivered.
FIND_SHIPMENTS_ACTIVE = """
SELECT s.shipment_id, 
"""

# Query for creating shipment after paying.
FIND_ADDRESS_BY_LOGIN = """
SELECT address
FROM users
WHERE login = %s;
"""

INSERT_SHIPMENT = """
INSERT INTO shipment (
    auction_id,
    address
)
VALUES (%s, %s)
"""

# Query for buyers to see won auctions
FIND_WON_AUCTIONS = """
SELECT 
    a.auction_id,
    i.item_name,
    i.category,
    i.description,
    a.current_highest_bid,
    a.auction_status
FROM auction a
JOIN item i ON a.item_id = i.item_id
WHERE a.winner_login = %s;
"""

# Query for browsing recent items listed on auction.
BROWSE_ITEMS = """
SELECT 
    a.auction_id,
    i.item_id,
    i.item_name,
    i.category,
    i.starting_price,
    a.current_highest_bid,
    a.seller_login
FROM auction a
JOIN item i ON i.item_id = a.item_id
WHERE a.auction_status = 'Active' AND a.seller_login <> %s
ORDER BY a.auction_id desc
LIMIT 10;
"""

# Query for buyers to see all item names, auctions, price for auctions they are winning.
GET_ACTIVE_BIDS = """
SELECT a.auction_id, i.item_name, i.category, a.current_highest_bid
FROM auction a
JOIN item i ON i.item_id = a.item_id
JOIN bid b ON b.auction_id = a.auction_id
WHERE a.auction_status = 'Active'
  AND b.buyer_login = %s
  AND b.bid_amount = a.current_highest_bid
ORDER BY i.item_name;
"""

# Queries for buyers to find auctions that they do not own and make bids.
FIND_AUCTION_BY_ITEM_NAME = """
SELECT 
    a.auction_id,
    i.item_id,
    a.current_highest_bid,
    i.starting_price,
    i.item_name,
    i.category,
    a.seller_login
FROM auction a
JOIN item i ON i.item_id = a.item_id
WHERE i.item_name LIKE %s
  AND a.seller_login <> %s
  AND a.auction_status = 'Active'
  AND NOT EXISTS (
      SELECT 1
      FROM bid b
      WHERE b.auction_id = a.auction_id
        AND b.buyer_login = %s
        AND b.bid_amount = a.current_highest_bid
  )
ORDER BY i.item_name
LIMIT 6;
"""

INSERT_BID = """
INSERT INTO bid (
    auction_id,
    buyer_login,
    bid_amount
)
VALUES (%s, %s, %s);
"""

UPDATE_CURR_HIGHEST_BID = """
UPDATE auction
SET current_highest_bid = %s
WHERE auction_id = %s;
"""


# Queries for buyers to view and make payments that are pending
GET_PENDING_PAYMENTS = """
SELECT p.payment_id, a.auction_id, i.item_name, p.amount
FROM payment p
JOIN auction a ON a.auction_id = p.auction_id
JOIN item i ON i.item_id = a.item_id
WHERE p.payment_status = 'Pending' AND p.buyer_login = %s
ORDER BY p.payment_id;
"""

SET_PAYMENT_STATUS_COMPLETED = """
UPDATE payment
SET payment_status = 'Completed'
WHERE payment_id = %s;
"""



# Queries for admin deleting item
GET_ITEM_DELETE_INFO = """
SELECT 
    i.item_id,
    i.item_name,
    i.category,
    i.seller_login,
    EXISTS (
        SELECT 1
        FROM auction a
        WHERE a.item_id = i.item_id
    ) AS has_auction
FROM item i
WHERE i.item_id = %s;
"""

DELETE_ITEM = """
DELETE FROM item
WHERE item_id = %s;
"""

# Queries for analytics in admin report
GET_USER_COUNT = """
SELECT COUNT(*)
FROM users;
"""

GET_NUM_BIDS_TODAY = """
SELECT COUNT(*)
FROM bid
WHERE bid_timestamp::date = CURRENT_DATE;
"""

GET_NUM_AUCTION = """
SELECT COUNT(*)
FROM auction;
"""

GET_NUM_AUCTION_ACTIVE = """
SELECT COUNT(*)
FROM auction
WHERE auction_status = 'Active';
"""

GET_MOST_BIDDED_AUCTIONS = """
SELECT 
    a.auction_id,
    i.item_name,
    COUNT(b.bid_id) AS num_bids
FROM auction a
JOIN item i ON i.item_id = a.item_id
LEFT JOIN bid b ON b.auction_id = a.auction_id
GROUP BY a.auction_id, i.item_name
ORDER BY num_bids DESC
LIMIT 5;
"""

GET_TOP_CATEGORIES_BY_BIDS = """
SELECT 
    i.category,
    COUNT(b.bid_id) AS num_bids
FROM item i
JOIN auction a ON a.item_id = i.item_id
JOIN bid b ON b.auction_id = a.auction_id
GROUP BY i.category
ORDER BY num_bids DESC
LIMIT 5;
"""

GET_TOP_SELLERS_BY_AUCTIONS = """
SELECT seller_login, COUNT(*) AS num_auctions
FROM auction
GROUP BY seller_login
ORDER BY num_auctions DESC
LIMIT 5;
"""

# For use in admin changing role screen.
SET_USER_ROLE = """
UPDATE users
SET role = %s
WHERE login = %s;
"""

GET_USER_BY_LOGIN = """
SELECT login, role
FROM users
WHERE login = %s;
"""

GET_USER_ROLE = """
SELECT role
FROM users
WHERE login = %s AND password = %s;
"""

# Get all items from seller that have never been in an auction
GET_POSS_ITEMS = """
SELECT i.item_id, i.item_name
FROM item i
WHERE i.seller_login = %s
  AND NOT EXISTS (
      SELECT 1
      FROM auction a
      WHERE a.item_id = i.item_id
  )
ORDER BY i.item_id;
"""

# Get all items from seller that are not in auction or have an 'Active' auction status
GET_POSS_ITEMS_ACTIVE = """
SELECT DISTINCT i.item_id, i.item_name
FROM item i
LEFT JOIN auction a ON a.item_id = i.item_id
WHERE i.seller_login = %s
  AND (
      a.item_id IS NULL
      OR a.auction_status = 'Active'
  )
ORDER BY i.item_id;
"""

# Update specific item
UPDATE_ITEM = """
UPDATE item
SET 
    item_name = %s,
    category = %s,
    starting_price = %s,
    image_url = %s,
    item_condition = %s,
    description = %s
WHERE item_id = %s
  AND seller_login = %s;
"""

GET_ITEM_BY_ID_FOR_SELLER = """
SELECT 
    item_name,
    category,
    starting_price,
    image_url,
    item_condition,
    description
FROM item
WHERE item_id = %s
  AND seller_login = %s;
"""

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
SELECT 
    item_id,
    item_name,
    category,
    starting_price,
    image_url,
    item_condition,
    description,
    seller_login
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









"""
Work on everything above
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

INSERT_AUCTION = """
INSERT INTO auction (
    item_id,
    seller_login
)
VALUES (%s, %s);
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