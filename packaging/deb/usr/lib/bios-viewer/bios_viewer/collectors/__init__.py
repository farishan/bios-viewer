# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Faris Han
"""Data collectors for the BIOS viewer (read-only)."""

from __future__ import annotations

from . import boot, dmi, ec, firmware, privileged, security, settings
from .privileged import merge_values
from .settings import collect_metadata, pending_reboot, save_settings_mode


def collect_all(read_values: bool = False) -> dict:
    """Collect everything. If read_values, attempt privileged read."""
    meta = collect_metadata()
    result = {
        "dmi": dmi.collect(),
        "settings": meta,
        "security": security.collect(),
        "boot": boot.collect(),
        "ec": ec.collect(),
        "firmware": firmware.collect(),
        "values_error": None,
    }
    if read_values:
        values, err = privileged.read_values()
        merge_values(meta, values)
        result["values_error"] = err
    else:
        # Mark all values unreadable.
        for s in meta.get("settings", []):
            s.setdefault("current_value", None)
            s.setdefault("value_readable", False)
    result["pending_reboot"] = pending_reboot(meta)
    result["save_settings"] = save_settings_mode(meta)
    return result


__all__ = [
    "boot", "dmi", "ec", "firmware", "privileged", "security", "settings",
    "collect_all", "collect_metadata", "merge_values",
]
