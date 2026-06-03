# Online Auction and Bidding System

This project is a PostgreSQL-backed auction marketplace application. Users can register, log in, browse items, search auctions, place bids, make payments, and manage shipments. The system supports three roles: Buyer, Seller, and Admin.

## Features

### Buyer
- Register and log in
- Browse active auction items
- Search auctions
- Place bids
- View active winning bids
- View won auctions
- Make payments
- Confirm delivered shipments
- Edit profile

### Seller
- Create items
- Update items
- Start auctions
- End auctions
- View recent auctions
- Ship items and add tracking numbers

### Admin
- Change user roles
- View site analytics
- Remove eligible items
- View recent payments
- View recent shipments

## Requirements

- Python 3
- PostgreSQL
- Python virtual environment
- Required Python packages listed in the project environment

## Startup Instructions

### 1. Activate the virtual environment.

```bash
source .venv/bin/activate
```

### 2. Run the Startup Script (Linux Only)

The startup script installs the required Python dependencies and PostgreSQL setup, then creates the project database tables and indexes.

```bash
chmod +x startup.sh
./startup.sh
```

### 3. Stop PostgreSQL services after running (Linux-only)

```bash
chmod +x stop.sh
./stop.sh
```

### 4. Leave the virtual environment

```bash
deactivate
```