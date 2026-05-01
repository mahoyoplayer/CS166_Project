DROP TABLE IF EXISTS account CASCADE;
DROP TABLE IF EXISTS item CASCADE;
DROP TABLE IF EXISTS payment CASCADE;
DROP TABLE IF EXISTS auction CASCADE;
DROP TABLE IF EXISTS shipment CASCADE;
DROP TABLE IF EXISTS bid CASCADE;

-- Check favorite category later
CREATE TABLE account (
    login VARCHAR(100) NOT NULL,
    phone_num CHAR(10) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'Buyer',
    password VARCHAR(100) NOT NULL,
    address VARCHAR(252) NOT NULL,
    fav_category VARCHAR(50),
    PRIMARY KEY (login),

    CONSTRAINT valid_role CHECK (role IN ('Buyer', 'Seller', 'Admin'))
);

CREATE TABLE item (
    item_id SERIAL NOT NULL,
    item_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    starting_price REAL NOT NULL,
    lister_login VARCHAR(100) NOT NULL,

    image_url TEXT,
    condition VARCHAR(100),
    description TEXT,
    
    PRIMARY KEY (item_id),
    FOREIGN KEY (lister_login) REFERENCES account(login) 
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT valid_start_price CHECK (starting_price >= 0)
);

-- Uh, confirm what happens when you delete user + auction
CREATE TABLE payment (
    payment_id SERIAL NOT NULL,
    login VARCHAR(100) NOT NULL,
    amount REAL NOT NULL,
    payment_status VARCHAR(20) NOT NULL,

    PRIMARY KEY (payment_id),
    FOREIGN KEY (login) REFERENCES account (login) 
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    CONSTRAINT valid_payment_status CHECK (payment_status IN ('Pending', 'Completed', 'Failed'))
);

-- Check what happpens for a winner delete
-- Should payment_id be unique?
CREATE TABLE auction (
    auction_id SERIAL NOT NULL,
    item_id INTEGER NOT NULL, 
    curr_highest_bid REAL,
    auction_status VARCHAR(20) NOT NULL,
    winner_login VARCHAR(100),
    payment_id INTEGER,

    PRIMARY KEY (auction_id),
    FOREIGN KEY (winner_login) REFERENCES account(login) 
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (payment_id) REFERENCES payment (payment_id) 
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (item_id) REFERENCES item (item_id) 
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT pos_curr_bid CHECK (curr_highest_bid >= 0),
    CONSTRAINT valid_auction_status CHECK (auction_status IN ('Active', 'Closed'))
);


-- Dependent on Auction
CREATE TABLE shipment (
    shipment_id SERIAL NOT NULL,
    auction_id INTEGER NOT NULL,
    address VARCHAR(100) NOT NULL,
    shipment_status VARCHAR(20) NOT NULL,
    tracking_no INTEGER,
    
    PRIMARY KEY (shipment_id),
    FOREIGN KEY (auction_id) REFERENCES auction (auction_id) 
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT valid_shipment_status CHECK (shipment_status IN ('Pending', 'Shipped', 'Delivered'))
);

-- Constraint role buyer or something
CREATE TABLE bid (
    bid_id SERIAL NOT NULL,
    auction_id INTEGER NOT NULL,
    bidder_login VARCHAR(100) NOT NULL,
    bid_amount REAL NOT NULL,
    bid_timestamp TIMESTAMP NOT NULL,
    
    PRIMARY KEY (bid_id),
    FOREIGN KEY (bidder_login) REFERENCES account(login)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (auction_id) REFERENCES auction(auction_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT pos_bid_amount CHECK (bid_amount > 0)
);


/*
Decimal: REAL
String: CHAR(int), VARCHAR(INT)

PRIMARY KEY (ssn),
FOREIGN KEY (ssn) REFERENCES Employee(ssn)


Constraints Syntax
CREATE TABLE Persons (
    ID int PRIMARY KEY,
    Age int,
    City VARCHAR(255),
    CONSTRAINT chk_PersonAge CHECK (Age >= 18 AND City = 'Sandnes')
);

Naming Practices - 
Everything lower case, _ for spaces like python

Auction

*/
