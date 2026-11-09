#!/usr/bin/env bash
# Manual (pip-free) local install of BIOS Viewer into ~/.local.
set -euo pipefail

PREFIX="${BIOS_VIEWER_PREFIX:-$HOME/.local}"
LIBDIR="$PREFIX/lib/bios-viewer"
BINDIR="$PREFIX/bin"
APPDIR="$PREFIX/share/applications"

mkdir -p "$LIBDIR" "$BINDIR" "$APPDIR"

# Copy package + assets
rm -rf "$LIBDIR/bios_viewer" "$LIBDIR/assets"
cp -r src/bios_viewer "$LIBDIR/bios_viewer"
cp -r assets "$LIBDIR/assets"

# Wrapper
cat > "$BINDIR/bios-viewer" <<'EOF'
#!/bin/sh
export PYTHONPATH="$HOME/.local/lib/bios-viewer${PYTHONPATH:+:$PYTHONPATH}"
export BIOS_VIEWER_ASSETS="$HOME/.local/lib/bios-viewer/assets"
exec python3 -m bios_viewer "$@"
EOF
chmod +x "$BINDIR/bios-viewer"

# Desktop entry
cat > "$APPDIR/bios-viewer.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=BIOS Viewer
Comment=Read-only BIOS/firmware settings viewer
Exec=$BINDIR/bios-viewer
Icon=applications-system
Terminal=false
Categories=System;Utility;
StartupNotify=true
EOF

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$APPDIR" 2>/dev/null || true
fi

echo "Installed BIOS Viewer to $PREFIX"
echo "Run: bios-viewer  (ensure $BINDIR is on PATH)"
