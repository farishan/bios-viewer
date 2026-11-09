# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Faris Han
import os

from bios_viewer.config import AppConfig


def test_from_env_overrides(monkeypatch, tmp_path):
    monkeypatch.setenv("BIOS_VIEWER_TITLE", "Hello")
    monkeypatch.setenv("BIOS_VIEWER_WIDTH", "800")
    monkeypatch.setenv("BIOS_VIEWER_HEIGHT", "600")
    monkeypatch.setenv("BIOS_VIEWER_ASSETS", str(tmp_path))
    cfg = AppConfig.from_env()
    assert cfg.title == "Hello"
    assert cfg.width == 800
    assert cfg.height == 600
    assert cfg.assets_dir == str(tmp_path)


def test_invalid_int_raises(monkeypatch):
    monkeypatch.setenv("BIOS_VIEWER_WIDTH", "nope")
    try:
        AppConfig.from_env()
    except ValueError as exc:
        assert "BIOS_VIEWER_WIDTH" in str(exc)
    else:
        raise AssertionError("expected ValueError")
