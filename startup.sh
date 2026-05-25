#!/usr/bin/env bash
set -e

DB_NAME="${1:-cs166_project}"

pip install -r requirements.txt

sudo systemctl start postgresql

echo "Generating fake data..."
python3 fake_data/generate_fake_data.py

echo "Loading fake data into $DB_NAME..."
psql "$DB_NAME" -f fake_data/fake_data_1000.sql

echo "Done."