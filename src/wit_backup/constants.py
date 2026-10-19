# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

# Package constants.

from enum import StrEnum


class Mode (StrEnum):
    """ Program operation modes.
    """
    BACKUP = "backup"
    RESTORE = "restore"
