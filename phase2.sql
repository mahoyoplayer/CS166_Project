DROP TABLE IF EXISTS USER;


CREATE TABLE User (
    login VARCHAR(100) NOT NULL,
    phoneNum CHAR(10) NOT NULL,
    role VARCHAR(20) NOT NULL,
    password VARCHAR(100) NOT NULL,
    address VARCHAR(252) NOT NULL,
    favoriteCategory CHAR,
    PRIMARY KEY (login)
);

-- Check what happpens for a winner delete
CREATE TABLE Auction (
    auctionId SERIAL NOT NULL,
    currentHighestBid REAL,
    auctionStatus VARCHAR(20) NOT NULL,
    winnerLogin VARCHAR(100)

    PRIMARY KEY (auctionId)
    FOREIGN KEY (winnerLogin) REFERENCES User(login) 
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Uh, confirm what happens when you delete user + auction
CREATE TABLE Payment (
    paymentId SERIAL NOT NULL,
    userLogin VARCHAR(100) NOT NULL,
    auctionId SERIAL NOT NULL,
    amount REAL NOT NULL,
    paymentStatus VARCHAR(20) NOT NULL,

    PRIMARY KEY (paymentId),
    FOREIGN KEY (userLogin) REFERENCES User(login) 
        ON DELETE CASCADE
        ON UPDATE CASCADE
    FOREIGN KEY (auctionId) REFERENCES Auction(auctionId) 
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Dependent on Auction
CREATE TABLE Shipment (
    shipmentId SERIAL NOT NULL,
    address VARCHAR(100) NOT NULL,
    shipmentStatus VARCHAR(20) NOT NULL,
    trackingNumber INTEGER,
    auctionId SERIAL NOT NULL,

    PRIMARY KEY (shipmentId),
    FOREIGN KEY (auctionId) REFERENCES Auction(auctionId) 
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE Bid (
    bidId SERIAL NOT NULL,
    bidderLogin VARCHAR(100) NOT NULL,
    bidAmount REAL NOT NULL,
    bidTimestamp date NOT NULL,
    auctionId SERIAL NOT NULL

    PRIMARY KEY (bidId),
    FOREIGN KEY (bidder_login) REFERENCES User(login)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    FOREIGN KEY (auctionId) REFERENCES Auction(auctionId)
        ON DELETE CASCADE
        ON UPDATE CASCADE
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

*/
