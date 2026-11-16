#!/bin/bash
# Builds the standalone PlaceHolder program with PyInstaller.
# Needs a virtual environment in ./venv with PyQt6 and PyInstaller:
#   python3 -m venv venv
#   ./venv/bin/pip install -r requirements.txt pyinstaller
set -e

if [ ! -f "icons/placeholder-icon.png" ]; then
    echo "ERROR: icons/placeholder-icon.png not found. Put the icons folder next to this script."
    exit 1
fi

echo "--- Cleaning previous build artifacts ---"
rm -rf build dist placeholder.spec

echo "--- Building with PyInstaller ---"
./venv/bin/python3 -m PyInstaller \
    --onefile \
    --noconsole \
    --name placeholder \
    --icon="icons/placeholder-icon.png" \
    --add-data "icons:icons" \
    placeholder.py

echo "--- Build complete! ---"
ls -lh dist/placeholder
