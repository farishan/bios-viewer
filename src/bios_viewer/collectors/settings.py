# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Faris Han
"""Firmware-attributes BIOS settings collector (metadata, no privilege)."""

from __future__ import annotations

import os
from typing import Any, Dict, List

ATTR_ROOT = "/sys/class/firmware-attributes"
# Special non-directory entries at the attribute root.
SPECIAL_NAMES = {"pending_reboot", "save_settings"}


def read_file(path: str) -> str | None:
    try:
        with open(path) as f:
            return f.read().strip()
    except (PermissionError, FileNotFoundError, OSError):
        return None


def _dedupe(values: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for v in values:
        v = v.strip()
        if v == "":
            continue
        if v in seen:
            continue
        seen.add(v)
        out.append(v)
    return out


def collect_metadata() -> Dict[str, Any]:
    """Return settings metadata (name, display_name, type, possible_values).

    Does NOT include current values (those require privilege).
    """
    result: Dict[str, Any] = {
        "root": ATTR_ROOT,
        "plugins": [],
        "special": {},
        "settings": [],
    }

    if not os.path.isdir(ATTR_ROOT):
        return result

    for plugin in sorted(os.listdir(ATTR_ROOT)):
        plugin_dir = os.path.join(ATTR_ROOT, plugin)
        if not os.path.isdir(plugin_dir):
            continue
        result["plugins"].append(plugin)
        attr_dir = os.path.join(plugin_dir, "attributes")
        if not os.path.isdir(attr_dir):
            continue

        for name in sorted(os.listdir(attr_dir)):
            full = os.path.join(attr_dir, name)
            if name in SPECIAL_NAMES or not os.path.isdir(full):
                # special file (pending_reboot, save_settings, etc.)
                val = read_file(full)
                result["special"][name] = val
                continue

            display = read_file(os.path.join(full, "display_name")) or name
            typ = read_file(os.path.join(full, "type")) or "unknown"
            possible_raw = read_file(os.path.join(full, "possible_values"))
            possible = _dedupe(possible_raw.split(";")) if possible_raw else []
            result["settings"].append({
                "plugin": plugin,
                "name": name,
                "display_name": display,
                "type": typ,
                "possible_values": possible,
            })

    return result


def pending_reboot(settings_meta: Dict[str, Any]) -> str | None:
    return settings_meta.get("special", {}).get("pending_reboot")


def save_settings_mode(settings_meta: Dict[str, Any]) -> str | None:
    return settings_meta.get("special", {}).get("save_settings")
