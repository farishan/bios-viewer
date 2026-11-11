# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Faris Han
"""Firmware devices and update history collector (fwupdmgr)."""

from __future__ import annotations

import json
import subprocess
from typing import Any, Dict, List


def _run_json(cmd: list[str]) -> Any:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def collect_devices() -> List[Dict[str, Any]]:
    data = _run_json(["fwupdmgr", "get-devices", "--json"])
    if not data:
        return []
    out: List[Dict[str, Any]] = []
    for d in data.get("Devices", []):
        out.append({
            "name": d.get("Name"),
            "version": d.get("Version"),
            "device_id": d.get("DeviceId"),
            "vendor": d.get("Vendor"),
            "serial": d.get("SerialNumber"),
            "updatable": d.get("UpdateState"),
        })
    return out


def collect_history() -> List[Dict[str, Any]]:
    data = _run_json(["fwupdmgr", "get-history", "--json"])
    if not data:
        return []
    # get-history returns a list of transactions under "History" or top-level.
    items = data.get("History") or data.get("Transactions") or []
    out: List[Dict[str, Any]] = []
    for h in items:
        out.append({
            "device": h.get("DeviceId") or h.get("Name"),
            "old_version": h.get("OldVersion"),
            "new_version": h.get("NewVersion"),
            "created": h.get("Created") or h.get("Timestamp"),
            "result": h.get("UpdateState") or h.get("Result"),
        })
    return out


def collect() -> Dict[str, Any]:
    return {
        "devices": collect_devices(),
        "history": collect_history(),
    }
