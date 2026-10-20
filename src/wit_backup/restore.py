# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

# Backup restoration functionality.

from logging import debug, info
from pathlib import Path


def traverse_recursive_restore (origin_dir: Path, target_dir: Path) -> None:
    """ 
    Main restore logic. Iterates recursively through folders comparing indexes
    and unzipping where indexes mismatch.
    """
    debug(f"===== traversing: {origin_dir}, {len(list(origin_dir.iterdir()))} items")
    
