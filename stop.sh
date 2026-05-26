#!/usr/bin/env bash
set -e

echo "Stopping PostgreSQL..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo systemctl stop postgresql 2>/dev/null || true

elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew services stop postgresql 2>/dev/null || true
    brew services stop postgresql@18 2>/dev/null || true
    brew services stop postgresql@17 2>/dev/null || true
    brew services stop postgresql@16 2>/dev/null || true

elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "win32"* ]]; then
    echo "Detected Windows Git Bash..."
    powershell.exe -Command "Get-Service postgresql* | Stop-Service -Force" 2>/dev/null || true
    taskkill //F //IM postgres.exe 2>/dev/null || true

else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

echo "Done."
read -p "Press Enter to close this window..."