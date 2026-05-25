#!/usr/bin/env bash
set -e

echo "Stopping PostgreSQL..."
sudo systemctl stop postgresql
echo "Done."