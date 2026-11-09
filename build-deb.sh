#!/usr/bin/env bash
# Build a .deb package for BIOS Viewer.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
STAGE="$ROOT/packaging/deb"
VERSION="${1:-0.1.0}"

# Prepare stage
mkdir -p "$STAGE"
find "$STAGE" -mindepth 1 -maxdepth 1 -exec rm -rf {} +

# Stage files
mkdir -p "$STAGE/DEBIAN" "$STAGE/usr/lib/bios-viewer" "$STAGE/usr/bin" "$STAGE/usr/share/applications"
cp -r "$ROOT/src/bios_viewer" "$STAGE/usr/lib/bios-viewer/bios_viewer"
cp -r "$ROOT/assets" "$STAGE/usr/lib/bios-viewer/assets"

# Wrapper
cat > "$STAGE/usr/bin/bios-viewer" <<'EOF'
#!/bin/sh
export PYTHONPATH="/usr/lib/bios-viewer${PYTHONPATH:+:$PYTHONPATH}"
export BIOS_VIEWER_ASSETS="/usr/lib/bios-viewer/assets"
exec python3 -m bios_viewer "$@"
EOF
chmod 755 "$STAGE/usr/bin/bios-viewer"

# Desktop entry
cat > "$STAGE/usr/share/applications/bios-viewer.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=BIOS Viewer
Comment=Read-only BIOS/firmware settings viewer
Exec=/usr/bin/bios-viewer
Icon=applications-system
Terminal=false
Categories=System;Utility;
StartupNotify=true
EOF

# Control file
cat > "$STAGE/DEBIAN/control" <<EOF
Package: bios-viewer
Version: $VERSION
Section: utils
Priority: optional
Architecture: all
Depends: python3, python3-gi, libgtk-3-0, libwebkit2gtk-4.0-37
Maintainer: Faris Han <faris@example.com>
Description: Read-only BIOS/firmware settings viewer for Linux
 Aggregates firmware-attributes, fwupd HSI, boot, EC, and firmware
 update history. Read-only by design.
EOF

# Build
mkdir -p "$ROOT/dist"
dpkg-deb --build "$STAGE" "$ROOT/dist/bios-viewer_${VERSION}_all.deb"
echo "Built: $ROOT/dist/bios-viewer_${VERSION}_all.deb"
