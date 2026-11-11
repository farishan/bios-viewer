# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Faris Han
"""WebKit2GTK 4.0 webview helpers."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Optional

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.0")
from gi.repository import Gtk, WebKit2  # type: ignore  # noqa: E402


def create_webview(
    assets_dir: str,
    on_message: Optional[Callable[[str], None]] = None,
    devtools: bool = False,
) -> WebKit2.WebView:
    """Create a WebKit2 4.0 webview pointed at the bundled index.html."""
    ucm = WebKit2.UserContentManager()
    if on_message is not None:
        ucm.register_script_message_handler("nativeApp")
        ucm.connect("script-message-received::nativeApp", lambda _ucm, msg: on_message(_extract_message(msg)))

    webview = WebKit2.WebView.new_with_user_content_manager(ucm)
    settings = webview.get_settings()
    settings.set_enable_developer_extras(devtools)
    settings.set_allow_file_access_from_file_urls(True)
    settings.set_allow_universal_access_from_file_urls(False)

    index = Path(assets_dir) / "index.html"
    if not index.is_file():
        raise FileNotFoundError(f"missing webview entry point: {index}")
    webview.load_uri(index.resolve().as_uri())
    return webview


def _extract_message(message: Any) -> str:
    # WebKit2.ScriptMessage API differs slightly across versions.
    for attr in ("get_js_value",):
        getter = getattr(message, attr, None)
        if callable(getter):
            try:
                js_value = getter()
                if hasattr(js_value, "to_string"):
                    return str(js_value.to_string())
            except Exception:  # pragma: no cover - defensive
                pass
    for attr in ("value", "js_value"):
        value = getattr(message, attr, None)
        if value is not None:
            try:
                return str(value.to_string() if hasattr(value, "to_string") else value)
            except Exception:  # pragma: no cover - defensive
                pass
    return str(message)


def run_javascript(webview: WebKit2.WebView, code: str) -> None:
    """Fire-and-forget JavaScript execution (compatible with WebKit2 4.0)."""
    try:
        webview.run_javascript(code, None, None, None)
    except TypeError:
        # Some bindings expect (script, cancellable, callback, user_data).
        webview.run_javascript(code, None, _noop_callback, None)


def _noop_callback(*_args: object) -> None:  # pragma: no cover - callback shim
    return None