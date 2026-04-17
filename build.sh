#!/usr/bin/env bash
# build.sh — Runs during Render build phase
set -e  # Exit immediately if any command fails

echo "🐍 Python version: $(python --version)"

echo "⬆️  Upgrading pip, setuptools and wheel..."
pip install --upgrade pip setuptools wheel

echo "📦 Installing dependencies (using pre-built wheels only)..."
# --prefer-binary: avoids compiling from source (no Rust/Cargo needed)
pip install --prefer-binary -r requirements.txt

echo "🤖 Pre-downloading EasyOCR English language models..."
python -c "
import easyocr
print('Downloading EasyOCR models...')
reader = easyocr.Reader(['en'], gpu=False)
print('✅ EasyOCR models ready.')
"

echo "✅ Build complete!"
