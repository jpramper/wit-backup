# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

""" Core functionality used for both backup and restore.
"""

import logging
from pathlib import Path
from shutil import rmtree

from .backup import (
    remove_target_outliers,
    traverse_recursive_backup,
)
from .constants import Mode
from .log import (
    log_timestamp,
)
from .restore import (
    traverse_recursive_restore,
)

logger = logging.getLogger(__name__)


def wary_backup_check (origin: Path, target: Path) -> bool:
    """ 
    Validates if origin is empty and target is not, returns true if so.
    This is important in case of a main drive failure, so a backup doesnt falsely
    clean a recurrent target backup to match a currently-empty origin.
    """
    return len(list(origin.iterdir())) == 0 and len(list(target.iterdir())) != 0


def wary_restore_check (target: Path) -> bool:
    """ 
    Validates if target is not empty, returns true if so.
    When restoring a backup, prevents overwriting existing trees by mistake.
    """
    return len(list(target.iterdir())) != 0


def clean_target (dest: Path) -> None:
    """ Ensures target directory is empty, if it exists.
    """
    logger.info(f"Cleaning target dir: {dest.resolve()}")
    if not dest.exists():
        logger.debug("Target did not exist; no need to clean")
        return
    for item in dest.iterdir():
        logger.debug(f"Subfolder {item} in target exists, nuking...")
        if item.is_dir() and not item.is_symlink():
            rmtree(item)
        else:
            item.unlink()
    logger.debug("Target cleaned")


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
        pass_protect: bool = False,
        password: str | None = None,
        ) -> int:
    """ Top-level backup logic.
    """
    target.mkdir(parents=True, exist_ok=True)

    if timestamp:
        ts_s = log_timestamp(target, Mode.BACKUP.value, "STARTED")
        logger.info(f"Backup started - {ts_s!s}")
    else:
        logger.info("Backup started.")
    logger.info(f"Origin: {origin.resolve()}")
    logger.info(f"Target: {target.resolve()}")

    if wary and wary_backup_check(origin, target) is True:
        logger.debug("SUSPICIOUS: origin is empty and target is not. Aborting.")
        return 5

    # First step is to iterate through target to trim those not in origin
    logger.debug("===== Cleaning folders in target not in origin")
    remove_target_outliers(target, origin)

    # Then ensure all folders in origin exist in target
    logger.debug("===== Mirror origin folder structure into target")
    reflect_directory_structure(origin, target)
    
    # Iterate through origin folders, indexing and backing up each
    traverse_recursive_backup(origin, target)

    if timestamp:
        ts_c = log_timestamp(target, Mode.BACKUP.value, "COMPLETED")
        logger.info(f"Backup completed - {ts_c!s}")
    else:
        logger.info("Backup completed.")

    return 0


def restore (
        origin: Path, 
        target: Path,
        wary: bool = False, 
        timestamp: bool = False,
        pass_protect: bool = False,
        password: str | None = None,
        ) -> int:
    """ Top-level restore logic.
    """
    target.mkdir(parents=True, exist_ok=True)

    if timestamp:
        ts_s = log_timestamp(target, Mode.RESTORE.value, "STARTED")
        logger.info(f"Restore started - {ts_s!s}")
    else:
        logger.info("Restore started.")
    logger.info(f"Origin: {origin.resolve()}")
    logger.info(f"Target: {target.resolve()}")

    if wary and wary_restore_check(target) is True:
        logger.debug("SUSPICIOUS: target is not empty upon restoring. Aborting.")
        return 6

    # Ensure all folders in origin exist in target
    logger.debug("===== Mirror origin folder structure into target")
    reflect_directory_structure(origin, target)
    
    # Iterate through origin folders, indexing and restoring each
    traverse_recursive_restore(origin, target)

    if timestamp:
        ts_c = log_timestamp(target, Mode.RESTORE.value, "COMPLETED")
        logger.info(f"Restore completed - {ts_c!s}")
    else:
        logger.info("Restore completed.")

    return 0