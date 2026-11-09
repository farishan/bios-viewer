# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Faris Han
"""Platform detection helpers.

The starter targets Ubuntu 22.04+ on X11. Some features (desktop-level
window hints) only work on X11; on Wayland we degrade gracefully instead of
crashing.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformInfo:
    session_type: str  # "x11", "wayland", or "unknown"
    is_x11: bool
    is_wayland: bool
    python: str


def detect() -> PlatformInfo:
    session = os.environ.get("XDG_SESSION_TYPE", "").strip().lower()
    if session not in {"x11", "wayland"}:
        # Fall back to common env hints.
        if os.environ.get("WAYLAND_DISPLAY"):
            session = "wayland"
        elif os.environ.get("DISPLAY"):
            session = "x11"
        else:
            session = "unknown"
    return PlatformInfo(
        session_type=session,
        is_x11=session == "x11",
        is_wayland=session == "wayland",
        python=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    )