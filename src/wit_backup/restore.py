# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

""" Backup restoration functionality.
"""

from logging import debug, info
from pathlib import Path
import zipfile

from .index import (
    create_index,
    read_index,
)
from .constants import (
    BACKUP_FILE,
    INDEX_FILE,
)


def unzip_contents (zip_file: Path, target_dir: Path) -> None:
    """ 
    Unzips all files in zipfile to dest.
    """
    info(f"Unipping {zip_file}.")
    with zipfile.ZipFile(zip_file, "r") as zip:
        zip.extractall(target_dir)


def traverse_recursive_restore (origin_dir: Path, target_dir: Path) -> None:
    """ 
    Main restore logic. Iterates recursively through folders comparing indexes
    and unzipping where indexes mismatch.
    """
    debug(f"===== traversing: {origin_dir}, {len(list(origin_dir.iterdir()))} items")

    origin_index = read_index(origin_dir / INDEX_FILE)
    target_index = create_index(target_dir)
    # compare index, store as "changed" if differ
    changed = origin_index != target_index
    debug(f"mismatched: {changed}")

    target_dir.mkdir(parents=True, exist_ok=True) # ensure target counterpart exists

    if changed and len(origin_index) > 0:
        debug(f"restoring {origin_dir}")
        unzip_contents((origin_dir / BACKUP_FILE), target_dir)

    for item in origin_dir.iterdir():
        if item.is_dir():
            traverse_recursive_restore(item, Path(target_dir, item.name))

