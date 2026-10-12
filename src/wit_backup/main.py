#!/usr/bin/env python3

# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

import logging
from pathlib import Path

from .args import (
    parse_args, 
    validate_origin_target,
    wary_backup_check,
)
from .backup import (
    clean_target,
    remove_target_outliers,
    reflect_directory_structure,
    traverse_recursive_backup,
)
from .log import (
    configure_logging,
    log_timestamp,
)


def backup (
        origin: Path, 
        target: Path, 
        wary: bool = False, 
        timestamp: bool = False
        ) -> int:
    """ Top-level backup logic.
    """
    logging.info("Backup started.")
    target.mkdir(parents=True, exist_ok=True)
    if timestamp:
        log_timestamp(target, "STARTED")

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

    logging.info("Backup completed.")
    if timestamp:
        log_timestamp(target, "COMPLETED")
    return 0


def restore (origin: Path, target: Path) -> int:
    """ Top-level restore logic.
    """
    logging.info("Restore started.")

    

    logging.info("Restore completed.")
    return 0


def main () -> int: # pragma: no cover
    """ Standard entrypoint
    """
    try:
        args = parse_args()
        validate_origin_target(args.origin, args.target)

        configure_logging(
            verbose=args.verbose, 
            quiet=args.quiet, 
            log_file=args.logfile
            )

        logging.info(f"Origin: {args.origin.resolve()}")
        logging.info(f"Target: {args.target.resolve()}")

        # Clean target if enabled, ensure target exists
        if args.delete:
            logging.debug("===== Delete option active; nuking target.")
            clean_target(args.target)

        if args.restore:
            restore(args.origin, args.target)
        else:
            backup(
                args.origin, 
                args.target, 
                wary=args.wary, 
                timestamp=args.timestamp
                )

    except Exception as e:
        # unexpected issues; extra logging for debugging
        logging.exception("Unexpected error")
        return 1

    return 0


def run (): # pragma: no cover
    exit(main())


if __name__ == "__main__": # pragma: no cover
    run()
