# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

""" Core functionality used for both backup and restore.
"""

import logging
from pathlib import Path
from shutil import rmtree

import pyzipper

from .backup import (
    remove_target_outliers,
    traverse_recursive_backup,
)
from .constants import (
    BACKUP_FILE,
    Mode,
)
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


def find_backup_file (target_dir: Path) -> Path | None:
    """ Recursively searches <target_dir> for a BACKUP_FILE.
    
    Returns the path to the first one found, or None if not found.
    """
    if not target_dir.is_dir():
        return None

    backup_file = Path(target_dir, BACKUP_FILE)
    if backup_file.is_file():
        return backup_file

    for item in target_dir.iterdir():
        if item.is_dir() and not item.is_symlink():
            found = find_backup_file(item)
            if found is not None:
                return found

    return None


def password_test (mode: Mode, target_dir: Path, password: str | None = None) -> bool:
    """ Validates that password supplied applies to archives in target.

    Recursively searches target_dir for a previous backup file. If none is found,
    fresh backup or restore is assumed and the test passes.
    If a backup file is found, ensures it is not password protected when no
    password is supplied, or that it is password protected and can be opened
    with the supplied password when one is.
    """
    backup_file = find_backup_file(target_dir)

    if backup_file is None:
        logger.info(f"No backup file found in target; assuming fresh {mode.value}.")
        return True

    logger.debug(f"Testing password against existing backup file: {backup_file}")

    with pyzipper.AESZipFile(backup_file, "r") as zip:
        protected = any(info.flag_bits & 0x1 for info in zip.infolist())

        if password is None:
            # ensure the archive is not password protected
            if protected:
                logger.error(
                    f"Backup file {backup_file} is password protected, "
                    "but no password was supplied."
                )
                return False
        elif not protected:
            # ensure the archive is password protected
            logger.error(
                f"Backup file {backup_file} is not password protected, "
                "but a password was supplied."
            )
            return False
        else:
            # ensure the archive can be opened with the supplied password
            zip.setpassword(password.encode())
            try:
                zip.testzip()
            except RuntimeError as e:
                logger.error(
                    f"Backup file {backup_file} could not be opened "
                    f"with the supplied password: {e}"
                )
                return False

    logger.info(f"Password test passed for {mode.value}.")
    return True


def backup (
        origin: Path, 
        target: Path, 
        wary: bool = False, 
        timestamp: bool = False,
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
    traverse_recursive_backup(origin, target, password)

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
    traverse_recursive_restore(origin, target, password)

    if timestamp:
        ts_c = log_timestamp(target, Mode.RESTORE.value, "COMPLETED")
        logger.info(f"Restore completed - {ts_c!s}")
    else:
        logger.info("Restore completed.")

    return 0