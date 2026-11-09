# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Faris Han
import os

from bios_viewer.platform import detect


def test_detect_x11(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    p = detect()
    assert p.is_x11 is True
    assert p.is_wayland is False
    assert p.session_type == "x11"


def test_detect_wayland(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    p = detect()
    assert p.is_wayland is True
    assert p.session_type == "wayland"
