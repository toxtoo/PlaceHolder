#!/bin/bash
#
# PlaceHolder installer (Linux)
#
#   ./install.sh              install PlaceHolder for the current user
#   ./install.sh --uninstall  remove it again
#
# Nothing here needs administrator rights. Everything goes into your own
# home folder:
#   ~/.local/share/placeholder/                       the program and its icon
#   ~/.local/share/applications/placeholder.desktop   the menu launcher

set -e

HERE="$(cd "$(dirname "$0")" && pwd)"
APPDIR="$HOME/.local/share/placeholder"
MENUDIR="$HOME/.local/share/applications"
LAUNCHER="$MENUDIR/placeholder.desktop"

refresh_menu() {
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "$MENUDIR" >/dev/null 2>&1 || true
    fi
}

if [ "$1" = "--uninstall" ]; then
    rm -rf "$APPDIR"
    rm -f "$LAUNCHER"
    refresh_menu
    echo "PlaceHolder has been removed from the menu and from $APPDIR."
    echo "Your settings in ~/.config/PlaceHolder were left alone."
    exit 0
fi

for needed in placeholder placeholder-icon.png; do
    if [ ! -f "$HERE/$needed" ]; then
        echo "ERROR: '$needed' was not found next to install.sh."
        echo "Run install.sh from inside the folder you extracted."
        exit 1
    fi
done

mkdir -p "$APPDIR" "$MENUDIR"

cp "$HERE/placeholder" "$APPDIR/placeholder"
cp "$HERE/placeholder-icon.png" "$APPDIR/placeholder-icon.png"
chmod +x "$APPDIR/placeholder"
chmod 644 "$APPDIR/placeholder-icon.png"

EXEC_PATH="$APPDIR/placeholder"
case "$EXEC_PATH" in
    *" "*) EXEC_PATH="\"$EXEC_PATH\"" ;;
esac

cat > "$LAUNCHER" <<EOF
[Desktop Entry]
Type=Application
Name=PlaceHolder
Comment=Make placeholder images for web pages
Exec=$EXEC_PATH
Icon=$APPDIR/placeholder-icon.png
Terminal=false
Categories=Graphics;Development;WebDevelopment;
EOF

chmod 644 "$LAUNCHER"
refresh_menu

echo "PlaceHolder is installed."
echo
echo "Look for PlaceHolder in your applications menu (under Graphics or"
echo "Programming). If it isn't there yet, log out and back in."
echo
echo "To remove it later, run:  ./install.sh --uninstall"
