#!/usr/bin/env bash
set -e

DB_NAME="${1:-cs166_project}"
SQL_FILE="fake_data_1000.sql"

echo "Generating fake auction data SQL..."
python3 generate_fake_data.py

echo "Loading data into database: $DB_NAME"
psql "$DB_NAME" -f "$SQL_FILE"

echo "Done. Inserted fake data."
