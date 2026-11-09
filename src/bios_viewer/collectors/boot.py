# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Faris Han
"""Boot configuration collector (efibootmgr + mokutil)."""

from __future__ import annotations

import re
import subprocess
from typing import Any, Dict, List


def _run(cmd: list[str]) -> str:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""
    return (proc.stdout or "") + (proc.stderr or "")


def collect() -> Dict[str, Any]:
    raw = _run(["efibootmgr"])
    boot_current = None
    timeout = None
    boot_order: List[str] = []
    entries: List[Dict[str, str]] = []
    for line in raw.splitlines():
        line = line.strip()
        m = re.match(r"BootCurrent:\s*(.+)", line)
        if m:
            boot_current = m.group(1).strip()
            continue
        m = re.match(r"Timeout:\s*(.+)", line)
        if m:
            timeout = m.group(1).strip()
            continue
        m = re.match(r"BootOrder:\s*(.+)", line)
        if m:
            boot_order = [x.strip() for x in m.group(1).split(",") if x.strip()]
            continue
        m = re.match(r"Boot([0-9A-Fa-f]+)\*?\s*(.*)", line)
        if m:
            entries.append({"id": m.group(1), "label": m.group(2).strip(), "active": "*" in line})
            continue

    sb_raw = _run(["mokutil", "--sb-state"])
    secure_boot = None
    for line in sb_raw.splitlines():
        if "SecureBoot" in line:
            secure_boot = line.strip()
            break

    return {
        "boot_current": boot_current,
        "timeout": timeout,
        "boot_order": boot_order,
        "entries": entries,
        "secure_boot": secure_boot,
        "raw": raw,
    }
