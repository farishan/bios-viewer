# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Faris Han
"""Main application window."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.0")
from gi.repository import Gtk, Gdk, WebKit2  # type: ignore  # noqa: E402

from .bridge import Bridge
from .config import AppConfig
from .logging import setup as setup_logging
from .platform import detect
from .webview import create_webview, run_javascript


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app: Gtk.Application, config: AppConfig, bridge: Bridge) -> None:
        super().__init__(application=app, title=config.title)
        self.config = config
        self.bridge = bridge
        self.log = setup_logging(config.log_level)

        self.set_default_size(config.width, config.height)
        self.set_size_request(config.min_width, config.min_height)
        if config.start_maximized:
            self.maximize()

        # Header bar (modern GNOME look).
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.set_title(config.title)
        self.set_titlebar(header)

        # Webview.
        self.webview = create_webview(
            config.assets_dir,
            on_message=self._on_web_message,
            devtools=config.devtools,
        )
        self.add(self.webview)

        self.connect("delete-event", self._on_delete)
        self.show_all()

        platform = detect()
        self.log.info("platform: %s (python %s)", platform.session_type, platform.python)
        if platform.is_wayland:
            self.log.warning(
                "Wayland session detected: X11-only window hints are unavailable."
            )

    def _on_web_message(self, raw: str) -> None:
        try:
            reply = self.bridge.dispatch(raw)
        except Exception as exc:  # bridge errors are user-facing
            self.log.warning("bridge error: %s", exc)
            reply = '{"ok": false, "error": "%s"}' % str(exc).replace('"', "'")
        run_javascript(self.webview, "window.nativeAppReceive && window.nativeAppReceive(" + reply + ");")

    def _on_delete(self, *_args: object) -> bool:
        self.log.info("window closing")
        return False  # allow destroy