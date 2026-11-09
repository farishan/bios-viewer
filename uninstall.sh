#!/usr/bin/env bash
set -euo pipefail
PREFIX="${BIOS_VIEWER_PREFIX:-$HOME/.local}"
rm -rf "$PREFIX/lib/bios-viewer"
rm -f "$PREFIX/bin/bios-viewer"
rm -f "$PREFIX/share/applications/bios-viewer.desktop"
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$PREFIX/share/applications" 2>/dev/null || true
fi
echo "Uninstalled BIOS Viewer from $PREFIX"
