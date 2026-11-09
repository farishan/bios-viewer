# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Faris Han
import json

from bios_viewer.bridge import Bridge, BridgeError


def test_dispatch_ping():
    b = Bridge()
    b.register("ping", lambda payload: {"pong": True})
    reply = json.loads(b.dispatch('{"action":"ping","payload":{}}'))
    assert reply["ok"] is True
    assert reply["result"]["pong"] is True


def test_unknown_action():
    b = Bridge()
    try:
        b.dispatch('{"action":"nope"}')
    except BridgeError:
        pass
    else:
        raise AssertionError("expected BridgeError")


def test_invalid_json():
    b = Bridge()
    try:
        b.dispatch("not json")
    except BridgeError:
        pass
    else:
        raise AssertionError("expected BridgeError")
