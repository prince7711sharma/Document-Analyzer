#!/usr/bin/env bash
# build.sh — Runs during Render build phase
# Pre-downloads EasyOCR English models so first request isn't delayed

set -e  # Exit immediately if a command fails

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🤖 Pre-downloading EasyOCR English language models..."
python -c "
import easyocr
print('Downloading EasyOCR models (this only happens once during build)...')
reader = easyocr.Reader(['en'], gpu=False)
print('✅ EasyOCR models downloaded successfully.')
"

echo "✅ Build complete!"
