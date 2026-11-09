# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Faris Han
"""GUI-free tests for collectors (run on any Linux with firmware-attributes)."""

from bios_viewer.collectors import dmi, ec, settings


def test_dmi_collect_returns_dict():
    data = dmi.collect()
    assert isinstance(data, dict)
    # On this machine these should exist.
    if data:
        assert "bios_vendor" in data or "sys_vendor" in data


def test_settings_metadata_shape():
    meta = settings.collect_metadata()
    assert "settings" in meta
    assert "special" in meta
    assert isinstance(meta["settings"], list)
    # All settings should have required keys.
    for s in meta["settings"]:
        assert "name" in s
        assert "type" in s
        assert "possible_values" in s
        assert isinstance(s["possible_values"], list)
    # possible_values should be de-duplicated.
    for s in meta["settings"]:
        vals = s["possible_values"]
        assert len(vals) == len(set(vals))


def test_ec_collect_shape():
    data = ec.collect()
    assert "available" in data
    assert "entries" in data
    if data["available"]:
        assert isinstance(data["entries"], dict)


def test_pending_reboot_value():
    meta = settings.collect_metadata()
    # pending_reboot special file should be readable as normal user.
    pr = settings.pending_reboot(meta)
    assert pr in (None, "0", "1")
