DROP INDEX IF EXISTS idx_users_role;

DROP INDEX IF EXISTS idx_item_seller_login;
DROP INDEX IF EXISTS idx_item_name_like;

DROP INDEX IF EXISTS idx_bid_auction_id;
DROP INDEX IF EXISTS idx_bid_timestamp;
DROP INDEX IF EXISTS idx_bid_buyer_auction_amount;

DROP INDEX IF EXISTS idx_auction_active;
DROP INDEX IF EXISTS idx_auction_winner_login;

DROP INDEX IF EXISTS idx_payment_buyer_status;
DROP INDEX IF EXISTS idx_payment_status;

CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- user indexes
CREATE INDEX idx_users_role
ON users(role);

-- item indexes
-- We often checked seller_login
CREATE INDEX idx_item_seller_login
ON item(seller_login);

-- For searching by item name
CREATE INDEX idx_item_name_like
ON item USING gin (item_name gin_trgm_ops);

-- Bid indexes
CREATE INDEX idx_bid_auction_id
ON bid(auction_id);

CREATE INDEX idx_bid_timestamp
ON bid(bid_timestamp);

CREATE INDEX idx_bid_buyer_auction_amount
ON bid(buyer_login, auction_id, bid_amount);

-- Auction indexes
-- For active auctions only
CREATE INDEX idx_auction_active 
ON auction (auction_status) 
WHERE auction_status = 'Active';

CREATE INDEX idx_auction_winner_login
ON auction(winner_login);


-- Payment indexes
-- For buyers looking at their pending payments
CREATE INDEX idx_payment_buyer_status
ON payment(buyer_login, payment_status)
WHERE payment_status = 'Pending';

-- For use in admin analytics
CREATE INDEX idx_payment_status
ON payment(payment_status);

-- Shipment indexes