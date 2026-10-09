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


def clean_target(dest: Path) -> None:
    """ Ensures target directory is empty, if it exists
    """
    info(f"Cleaning target dir: {dest.resolve()}")
    if not dest.exists():
        debug("Target did not exist; no need to clean")
        return
    for item in dest.iterdir():
        debug(f"Subfolder {item} in target exists, nuking...")
        if item.is_dir() and not item.is_symlink():
            rmtree(item)
        else:
            item.unlink()
    debug("Target cleaned")


def remove_target_outliers (target_dir: Path, origin_dir: Path) -> None:
    """ Traverses through <target> tree, removing folders not present in <origin>.
    It purposely does not remove files since that would nuke all backup/index files in target.
    """
    for item in target_dir.iterdir():
        origin_equivalent = Path(origin_dir, item.name)

        if item.is_dir() and not origin_equivalent.exists():
            info(f"Folder {item} is not in {origin_dir}; removing.")
            if item.is_symlink():
                item.unlink()
            else:
                rmtree(item)

        if item.is_dir():
            remove_target_outliers(item, origin_equivalent)


def reflect_directory_structure(origin_dir: Path, target_dir: Path) -> None:
    """ Ensures <target> folders exist in <origin>
    """
    for item in origin_dir.iterdir():
        if item.is_dir() and not item.is_symlink():
            target_equivalent = Path(target_dir, item.name)
            target_equivalent.mkdir(parents=True, exist_ok=True)
            reflect_directory_structure(item, target_equivalent)


def zip_contents(origin_dir: Path, target_dir: Path) -> None:
    """ Zips all files in origin to dest"""
    info(f"Zipping {origin_dir} to backup.")
    zip_file = Path(target_dir, BACKUP_FILE)
    with zipfile.ZipFile(zip_file, mode="w", compression=zipfile.ZIP_DEFLATED) as zip:
        for item in origin_dir.iterdir():
            if item.is_file():
                zip.write(item, arcname=item.name)


def traverse_recursive_backup(origin_dir: Path, target_dir: Path) -> None:
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
