#!/bin/bash
#
# Packs the built PlaceHolder into one download for GitHub Releases.
# Run it after ./build.sh has finished:
#
#   ./make-release.sh 1.1      makes release/placeholder-linux-v1.1.tar.gz

set -e

VERSION="${1:-1.1}"
NAME="placeholder-linux-v$VERSION"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

PROGRAM="dist/placeholder"
ICON="icons/placeholder-icon.png"

if [ ! -f "$PROGRAM" ]; then
    echo "ERROR: $PROGRAM not found. Run ./build.sh first."
    exit 1
fi

for needed in "$ICON" "$SCRIPT_DIR/install.sh"; do
    if [ ! -f "$needed" ]; then
        echo "ERROR: $needed not found."
        exit 1
    fi
done

rm -rf "release/$NAME" "release/$NAME.tar.gz"
mkdir -p "release/$NAME"

cp "$PROGRAM" "release/$NAME/placeholder"
cp "$ICON" "release/$NAME/placeholder-icon.png"
cp "$SCRIPT_DIR/install.sh" "release/$NAME/install.sh"
chmod +x "release/$NAME/placeholder" "release/$NAME/install.sh"

cat > "release/$NAME/README.txt" <<EOF
PlaceHolder $VERSION (Linux, 64-bit)

Makes plain placeholder images for laying out web pages.

To install:
  1. Extract this archive.
  2. Open a terminal in the extracted folder.
  3. Run:  ./install.sh

PlaceHolder then appears in your applications menu.

To remove it:  ./install.sh --uninstall
EOF

tar -C release -czf "release/$NAME.tar.gz" "$NAME"

echo
echo "Release file created:"
ls -lh "release/$NAME.tar.gz"
