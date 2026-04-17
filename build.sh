#!/usr/bin/env bash
# build.sh — Runs during Render build phase
set -e  # Exit immediately if any command fails

echo "⬆️  Upgrading pip, setuptools and wheel first..."
pip install --upgrade pip setuptools wheel

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🤖 Pre-downloading EasyOCR English language models..."
python -c "
import easyocr
print('Downloading EasyOCR models (this only happens once during build)...')
reader = easyocr.Reader(['en'], gpu=False)
print('✅ EasyOCR models downloaded successfully.')
"

echo "✅ Build complete!"
