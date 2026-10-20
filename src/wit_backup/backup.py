# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

# Core backup functionality.

from pathlib import Path
from logging import debug, info
from shutil import rmtree
import zipfile

from .index import (
    create_index, 
    write_index,
    indexes_mismatch,
)


BACKUP_FILE = "_backup_.zip"


def remove_target_outliers (target_dir: Path, origin_dir: Path) -> None:
    """ Traverses through <target> tree, removing folders not present in <origin>.
    It purposely does not remove files since that would nuke all backup/index files in target.
    """
    for item in target_dir.iterdir():
        origin_equivalent = Path(origin_dir, item.name)

        # symlinks must be handled first since is_dir stops 
        # detecting them when their target is gone
        if item.is_symlink() and not origin_equivalent.exists():
            info(f"Symlink {item} is not in {origin_dir}; removing.")
            item.unlink()
            continue

        if item.is_dir() and not origin_equivalent.exists():
            info(f"Folder {item} is not in {origin_dir}; removing.")
            rmtree(item)
            continue

        if item.is_dir():
            remove_target_outliers(item, origin_equivalent)


def zip_contents (origin_dir: Path, target_dir: Path) -> Path:
    """ 
    Zips all files in origin to dest.
    Returns a path to the zipfile if created. Empty Path if no zipfile was created.
    """
    info(f"Zipping {target_dir / BACKUP_FILE}.")
    zip_file = Path(target_dir, BACKUP_FILE)

    if origin_dir.resolve() == target_dir.resolve():
        return zip_file

    has_files = False
    for item in origin_dir.iterdir():
        if item.is_file():
            has_files = True
            break

    if has_files:
        # ensure target exists
        target_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_file, mode="w", compression=zipfile.ZIP_DEFLATED) as zip:
            for item in origin_dir.iterdir():
                if item.is_file():
                    zip.write(item, arcname=item.name)

    return zip_file


def traverse_recursive_backup (origin_dir: Path, target_dir: Path) -> None:
    """ 
    Main backup logic. Iterates recursively through folders comparing indexes
    and backing up where indexes mismatch.
    """
    debug(f"===== traversing: {origin_dir}, {len(list(origin_dir.iterdir()))} items")
    for item in origin_dir.iterdir():
        debug(f"{"d" if item.is_dir() else "f"} {Path(item.name)} ")

    origin_index = create_index(origin_dir)
    # compare index, store as "changed" if differ (return boolean)
    changed = indexes_mismatch(origin_index, target_dir)
    debug(f"mismatched: {changed}")

    target_dir.mkdir(parents=True, exist_ok=True) # ensure target counterpart exists

    if changed:
        write_index(origin_index, target_dir)

    if changed and len(origin_index) > 0:
        debug(f"backing up for {origin_dir}")
        if (len(origin_index) > 0):
            zip_contents(origin_dir, target_dir)

    for item in origin_dir.iterdir():
        if item.is_dir():
            traverse_recursive_backup(item, Path(target_dir, item.name))
