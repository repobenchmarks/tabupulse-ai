#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "--- Installing Python Backend Dependencies ---"
pip install --upgrade pip
pip install -r requirements.txt

echo "--- Building React Frontend with Vite ---"
cd frontend
npm ci || npm install
npm run build
cd ..

echo "--- Build Finished Successfully ---"
