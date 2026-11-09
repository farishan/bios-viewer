# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Faris Han
"""Privileged BIOS current-value reader via pkexec + fwupdmgr.

Values require polkit admin auth. Degrades gracefully when auth is denied.
"""

from __future__ import annotations

import json
import subprocess
from typing import Dict, Tuple


def read_values() -> Tuple[Dict[str, str], str | None]:
    """Return (name->current_value, error_or_None).

    Tries pkexec first (graphical prompt), then sudo -n (non-interactive).
    """
    for cmd in (
        ["pkexec", "fwupdmgr", "get-bios-settings", "--json"],
        ["sudo", "-n", "fwupdmgr", "get-bios-settings", "--json"],
    ):
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except FileNotFoundError:
            continue
        except subprocess.TimeoutExpired:
            return {}, "timed out reading BIOS settings"
        if proc.returncode != 0:
            err = (proc.stderr or "").strip() or f"exit {proc.returncode}"
            # Try next method.
            last_err = err
            continue
        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            return {}, f"invalid JSON from fwupdmgr: {exc}"
        values: Dict[str, str] = {}
        for item in data.get("BiosSettings", []):
            name = item.get("Name")
            val = item.get("BiosSettingCurrentValue")
            if name is not None and val is not None:
                values[name] = str(val)
        return values, None
    return {}, (last_err if 'last_err' in locals() else "unable to read BIOS values (auth required)")


def merge_values(settings_meta: dict, values: Dict[str, str]) -> None:
    """Attach current_value to each setting in place."""
    for s in settings_meta.get("settings", []):
        name = s.get("name")
        if name in values:
            s["current_value"] = values[name]
            s["value_readable"] = True
        else:
            s["current_value"] = None
            s["value_readable"] = False
