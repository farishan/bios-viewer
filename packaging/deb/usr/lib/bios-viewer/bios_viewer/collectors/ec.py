# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Faris Han
"""ThinkPad embedded-controller (thinkpad_acpi) collector."""

from __future__ import annotations

import os
from typing import Any, Dict

EC_ROOT = "/proc/acpi/ibm"


def read_file(path: str) -> str:
    try:
        with open(path) as f:
            return f.read().strip()
    except (PermissionError, FileNotFoundError, OSError):
        return ""


def _parse_kv(text: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for line in text.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            out[key.strip()] = val.strip()
    return out


def collect() -> Dict[str, Any]:
    result: Dict[str, Any] = {"available": os.path.isdir(EC_ROOT), "entries": {}}
    if not result["available"]:
        return result
    for name in sorted(os.listdir(EC_ROOT)):
        path = os.path.join(EC_ROOT, name)
        if not os.path.isfile(path):
            continue
        result["entries"][name] = _parse_kv(read_file(path))
    return result
