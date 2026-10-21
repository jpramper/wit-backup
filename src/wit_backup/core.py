# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

""" Core functionality used for both backup and restore.
"""

import logging
from pathlib import Path
from shutil import rmtree

from .constants import Mode
from .backup import (
    remove_target_outliers,
    traverse_recursive_backup,
)
from .restore import (
    traverse_recursive_restore,
)
from .log import (
    log_timestamp,
)


def wary_backup_check (origin: Path, target: Path) -> bool:
    """ 
    Validates if origin is empty and target is not, returns true if so.
    This is important in case of a main drive failure, so a backup doesnt falsely
    clean a recurrent target backup to match a currently-empty origin.
    """
    if len(list(origin.iterdir())) == 0 and len(list(target.iterdir())) != 0:
        return True

    return False


def wary_restore_check (target: Path) -> bool:
    """ 
    Validates if target is not empty, returns true if so.
    When restoring a backup, prevents overwriting existing trees by mistake.
    """
    if len(list(target.iterdir())) != 0:
        return True

    return False


def clean_target (dest: Path) -> None:
    """ Ensures target directory is empty, if it exists.
    """
    logging.info(f"Cleaning target dir: {dest.resolve()}")
    if not dest.exists():
        logging.debug("Target did not exist; no need to clean")
        return
    for item in dest.iterdir():
        logging.debug(f"Subfolder {item} in target exists, nuking...")
        if item.is_dir() and not item.is_symlink():
            rmtree(item)
        else:
            item.unlink()
    logging.debug("Target cleaned")


def reflect_directory_structure (origin_dir: Path, target_dir: Path) -> None:
    """ Ensures <target> folders exist in <origin>.
    """
    for item in origin_dir.iterdir():
        if item.is_dir() and not item.is_symlink():
            target_equivalent = Path(target_dir, item.name)
            target_equivalent.mkdir(parents=True, exist_ok=True)
            reflect_directory_structure(item, target_equivalent)


def backup (
        origin: Path, 
        target: Path, 
        wary: bool = False, 
        timestamp: bool = False,
        ) -> int:
    """ Top-level backup logic.
    """
    target.mkdir(parents=True, exist_ok=True)

    if timestamp:
        ts_s = log_timestamp(target, Mode.BACKUP.value, "STARTED")
        logging.info(f"Backup started - {str(ts_s)}")
    else:
        logging.info(f"Backup started.")
    logging.info(f"Origin: {origin.resolve()}")
    logging.info(f"Target: {target.resolve()}")

    if wary:
        if wary_backup_check(origin, target) is True:
            logging.debug("SUSPICIOUS: origin is empty and target is not. Aborting.")
            return 5

    # First step is to iterate through target to trim those not in origin
    logging.debug("===== Cleaning folders in target not in origin")
    remove_target_outliers(target, origin)

    # Then ensure all folders in origin exist in target
    logging.debug("===== Mirror origin folder structure into target")
    reflect_directory_structure(origin, target)
    
    # Iterate through origin folders, indexing and backing up each
    traverse_recursive_backup(origin, target)

    if timestamp:
        ts_c = log_timestamp(target, Mode.BACKUP.value, "COMPLETED")
        logging.info(f"Backup completed - {str(ts_c)}")
    else:
        logging.info("Backup completed.")

    return 0


def restore (
        origin: Path, 
        target: Path,
        wary: bool = False, 
        timestamp: bool = False,
        ) -> int:
    """ Top-level restore logic.
    """
    target.mkdir(parents=True, exist_ok=True)

    if timestamp:
        ts_s = log_timestamp(target, Mode.RESTORE.value, "STARTED")
        logging.info(f"Restore started - {str(ts_s)}")
    else:
        logging.info(f"Restore started.")
    logging.info(f"Origin: {origin.resolve()}")
    logging.info(f"Target: {target.resolve()}")

    if wary:
        if wary_restore_check(target) is True:
            logging.debug("SUSPICIOUS: target is not empty upon restoring. Aborting.")
            return 6

    # Ensure all folders in origin exist in target
    logging.debug("===== Mirror origin folder structure into target")
    reflect_directory_structure(origin, target)
    
    # Iterate through origin folders, indexing and restoring each
    traverse_recursive_restore(origin, target)

    if timestamp:
        ts_c = log_timestamp(target, Mode.RESTORE.value, "COMPLETED")
        logging.info(f"Restore completed - {str(ts_c)}")
    else:
        logging.info("Restore completed.")

    return 0