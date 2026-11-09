# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Faris Han
"""Logging setup for the starter."""

from __future__ import annotations

import logging
import sys


def setup(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("bios_viewer")
    if logger.handlers:
        return logger
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    logger.addHandler(handler)
    logger.propagate = False
    return logger