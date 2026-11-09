# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Faris Han
"""fwupd host security (HSI) collector (no privilege needed)."""

from __future__ import annotations

import json
import subprocess
from typing import Any, Dict


def _run_json(cmd: list[str]) -> Tuple[Any, str | None]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        return None, f"command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return None, "timed out"
    if proc.returncode != 0:
        return None, (proc.stderr or "").strip() or f"exit {proc.returncode}"
    try:
        return json.loads(proc.stdout), None
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}"


from typing import Tuple


def collect() -> Dict[str, Any]:
    data, err = _run_json(["fwupdmgr", "security", "--json"])
    if err:
        return {"error": err, "attributes": [], "events": []}
    attrs = []
    for a in data.get("SecurityAttributes", []):
        attrs.append({
            "name": a.get("Name"),
            "summary": a.get("Summary"),
            "hsi_result": a.get("HsiResult"),
            "success": a.get("HsiResultSuccess"),
            "flags": a.get("Flags", []),
            "uri": a.get("Uri"),
        })
    events = []
    for e in data.get("SecurityEvents", []):
        events.append({
            "created": e.get("Created"),
            "name": e.get("Name"),
            "result": e.get("HsiResult"),
            "summary": e.get("Summary"),
        })
    return {"attributes": attrs, "events": events, "error": None}
