#!/bin/bash
set -e

# Make sure we run from project directory
cd "$(dirname "$0")"

echo "=== 1. Generating icons (ICO & ICNS) ==="
.venv/bin/python assets/make_icon.py

echo "=== 2. Installing PyInstaller in virtual environment ==="
.venv/bin/pip install pyinstaller

echo "=== 3. Cleaning old build artifacts ==="
rm -rf build dist

echo "=== 4. Building macOS App Bundle via PyInstaller ==="
.venv/bin/pyinstaller maclicky.spec --clean --noconfirm

echo "=== 5. Packaging into a DMG installer ==="
# Create direct DMG from the App Bundle
hdiutil create -fs HFS+ -srcfolder dist/Maclicky.app -volname "Maclicky" dist/Maclicky.dmg

echo "=== 6. Packaging into a ZIP archive ==="
cd dist
zip -r -q Maclicky-macOS.zip Maclicky.app
cd ..

echo "============================================="
echo "Build complete!"
echo "Outputs created in dist/:"
echo "  - dist/Maclicky.app      (Local macOS application)"
echo "  - dist/Maclicky.dmg      (Double-clickable Disk Image installer)"
echo "  - dist/Maclicky-macOS.zip (ZIP compressed archive)"
echo "============================================="
