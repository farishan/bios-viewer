# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Faris Han
"""Application entry point."""

from __future__ import annotations

import sys

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # type: ignore  # noqa: E402

from .bridge import Bridge
from .config import AppConfig
from .logging import setup as setup_logging
from .window import MainWindow


def build_bridge() -> Bridge:
    bridge = Bridge()

    def ping(_payload: dict) -> dict:
        return {"pong": True}

    def get_identity(_payload: dict) -> dict:
        from .collectors import dmi

        return {"identity": dmi.collect()}

    def get_settings(payload: dict) -> dict:
        from .collectors import privileged
        from .collectors import settings as sc
        read_values = bool(payload.get("read_values", False)) if isinstance(payload, dict) else False
        meta = sc.collect_metadata()
        values_error = None
        if read_values:
            values, err = privileged.read_values()
            privileged.merge_values(meta, values)
            values_error = err
        else:
            for st in meta.get("settings", []):
                st.setdefault("current_value", None)
                st.setdefault("value_readable", False)
        return {
            "settings": meta,
            "pending_reboot": sc.pending_reboot(meta),
            "save_settings": sc.save_settings_mode(meta),
            "values_error": values_error,
        }

    def get_security(_payload: dict) -> dict:
        from .collectors import security

        return {"security": security.collect()}

    def get_boot(_payload: dict) -> dict:
        from .collectors import boot

        return {"boot": boot.collect()}

    def get_ec(_payload: dict) -> dict:
        from .collectors import ec

        return {"ec": ec.collect()}

    def get_firmware(_payload: dict) -> dict:
        from .collectors import firmware

        return {"firmware": firmware.collect()}

    bridge.register("ping", ping)
    bridge.register("get_identity", get_identity)
    bridge.register("get_settings", get_settings)
    bridge.register("get_security", get_security)
    bridge.register("get_boot", get_boot)
    bridge.register("get_ec", get_ec)
    bridge.register("get_firmware", get_firmware)
    return bridge


class Application(Gtk.Application):
    def __init__(self, config: AppConfig) -> None:
        super().__init__(application_id=config.app_id)
        self.config = config
        self.bridge = build_bridge()
        self.window: MainWindow | None = None

    def do_activate(self) -> None:
        if self.window is None:
            self.window = MainWindow(self, self.config, self.bridge)
        self.window.present()


def main(argv: list[str] | None = None) -> int:
    config = AppConfig.from_env()
    log = setup_logging(config.log_level)
    log.info("starting %s", config.app_id)
    app = Application(config)
    return app.run(argv if argv is not None else sys.argv[1:])
