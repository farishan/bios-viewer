# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Faris Han
"""DMI/SMBIOS identity collector (no privilege needed)."""

from __future__ import annotations

import os
from typing import Dict

DMI_ROOT = "/sys/class/dmi/id"

KEYS = [
    "sys_vendor", "product_name", "product_family", "product_version",
    "product_sku", "bios_vendor", "bios_version", "bios_date",
    "board_vendor", "board_name", "board_version",
    "chassis_vendor", "chassis_type", "chassis_version",
]


def read_file(path: str) -> str | None:
    try:
        with open(path) as f:
            return f.read().strip()
    except (PermissionError, FileNotFoundError, OSError):
        return None


def collect() -> Dict[str, str]:
    out: Dict[str, str] = {}
    for key in KEYS:
        value = read_file(os.path.join(DMI_ROOT, key))
        if value is not None and value != "":
            out[key] = value
    return out
