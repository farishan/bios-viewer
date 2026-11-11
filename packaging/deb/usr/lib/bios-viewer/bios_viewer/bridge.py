# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Faris Han
"""JavaScript <-> Python bridge for the WebKit webview.

The bridge is intentionally tiny and explicit: every message from the UI is
validated and dispatched by name. Never expose arbitrary Python execution to
the webview.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict


class BridgeError(Exception):
    """Raised when a bridge message is malformed or unknown."""


Handler = Callable[[Dict[str, Any]], Any]


class Bridge:
    def __init__(self) -> None:
        self._handlers: Dict[str, Handler] = {}

    def register(self, name: str, handler: Handler) -> None:
        if not name or not name.isidentifier():
            raise ValueError(f"invalid handler name: {name!r}")
        self._handlers[name] = handler

    def dispatch(self, raw: str) -> str:
        """Dispatch a JSON message from the webview and return a JSON reply."""
        try:
            message = json.loads(raw)
        except (json.JSONDecodeError, TypeError) as exc:
            raise BridgeError(f"invalid JSON: {exc}") from exc

        if not isinstance(message, dict):
            raise BridgeError("message must be a JSON object")
        name = message.get("action")
        if not isinstance(name, str) or name not in self._handlers:
            raise BridgeError(f"unknown action: {name!r}")

        payload = message.get("payload", {})
        if not isinstance(payload, (dict, list, str, int, float, bool, type(None))):
            raise BridgeError("payload must be JSON-serialisable")
        result = self._handlers[name](payload if isinstance(payload, dict) else {"value": payload})
        return json.dumps({"ok": True, "result": result})

    def actions(self) -> list[str]:
        return sorted(self._handlers)