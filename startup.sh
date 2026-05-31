#!/usr/bin/env bash
# Exit on error, but show the error line and pause before closing
set -e
trap 'echo "ERROR at line $LINENO: $BASH_COMMAND (exit code: $?)"; read -p "Press Enter to exit..."; exit 1' ERR

DB_NAME="${1:-cs166_final}"

echo "Installing Python requirements..."
if ! command -v pip >/dev/null 2>&1; then
    echo "pip not found. Please install pip first."
    exit 1
fi
if [ ! -f "requirements.txt" ]; then
    echo "requirements.txt not found in current directory."
    exit 1
fi
pip install -r requirements.txt

# Detect Python command
PYTHON_CMD="python3"
if [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "win32"* ]]; then
    PYTHON_CMD="python"
fi

echo "Checking PostgreSQL..."
if ! command -v psql >/dev/null 2>&1; then
    echo "PostgreSQL not found. Installing..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt update
        sudo apt install -y postgresql postgresql-contrib
        sudo systemctl enable postgresql
        sudo systemctl start postgresql
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install postgresql
        brew services start postgresql
    elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "win32"* ]]; then
        winget install -e --id PostgreSQL.PostgreSQL
        echo "Installed PostgreSQL. Restart Git Bash and run this script again."
        read -p "Press Enter to exit..."
        exit 0
    else
        echo "Unsupported OS: $OSTYPE"
        exit 1
    fi
    # Wait a moment for PostgreSQL to initialise
    sleep 3
fi

# Start PostgreSQL if not running (Linux/macOS)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo systemctl start postgresql
elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew services start postgresql
fi

# ----- PostgreSQL authentication fix -----
# Use 'postgres' superuser for all DB commands on Unix systems
if [[ "$OSTYPE" != "msys"* && "$OSTYPE" != "win32"* ]]; then
    PSQL_CMD="sudo -u postgres psql"
    CREATEDB_CMD="sudo -u postgres createdb"
else
    PSQL_CMD="psql"
    CREATEDB_CMD="createdb"
fi

echo "Creating database '$DB_NAME' if it doesn't exist..."
DB_EXISTS=$($PSQL_CMD -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';" 2>/dev/null || echo "")
if [[ "$DB_EXISTS" == "1" ]]; then
    echo "Database '$DB_NAME' already exists."
else
    $CREATEDB_CMD "$DB_NAME"
    echo "Database '$DB_NAME' created."
fi

echo "Creating tables..."
if [ ! -f "data_setup/create_tables.sql" ]; then
    echo "Missing data_setup/create_tables.sql"
    exit 1
fi
$PSQL_CMD -d "$DB_NAME" -v ON_ERROR_STOP=1 -f data_setup/create_tables.sql

echo "Creating indexes..."
if [ ! -f "data_setup/create_indexes.sql" ]; then
    echo "Missing data_setup/create_indexes.sql"
    exit 1
fi
$PSQL_CMD -d "$DB_NAME" -v ON_ERROR_STOP=1 -f data_setup/create_indexes.sql

#echo "Generating fake data..."
#if [ ! -f "data_setup/generate_fake_data.py" ]; then
#    echo "Missing data_setup/generate_fake_data.py"
#    exit 1
#fi
#$PYTHON_CMD data_setup/generate_fake_data.py

echo "Loading fake data into $DB_NAME..."
if [ ! -f "data_setup/fake_data_1000.sql" ]; then
    echo "Missing data_setup/fake_data_1000.sql"
    exit 1
fi
$PSQL_CMD -d "$DB_NAME" -v ON_ERROR_STOP=1 -f data_setup/fake_data_1000.sql

echo "Startup complete. All good."
read -p "Press Enter to close this window..."