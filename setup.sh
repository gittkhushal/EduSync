#!/usr/bin/env bash
# setup.sh — EduSync v2 setup for Linux / macOS
set -e

echo "=============================================="
echo " EduSync v2 — Setup"
echo "=============================================="

# Create venv
if [ ! -d ".venv" ]; then
    echo "[1/3] Creating virtual environment..."
    python3 -m venv .venv
fi

# Install deps
echo "[2/3] Installing flask + cffi..."
source .venv/bin/activate
pip install --quiet --upgrade flask cffi

# Check for compiler
if command -v gcc &>/dev/null || command -v clang &>/dev/null; then
    echo "[3/3] Compiler found — C acceleration enabled."
else
    echo "[3/3] No compiler found — running in pure Python mode."
fi

echo ""
echo "=============================================="
echo " Starting EduSync at http://127.0.0.1:5000"
echo " Login: student / 123   or   teacher / 123"
echo "=============================================="
python3 app.py
