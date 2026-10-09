#!/usr/bin/env python3

# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

import logging
from pathlib import Path

from .args import parse_args, validate_origin_target
from .backup import (
  clean_target,
  remove_target_outliers,
  reflect_directory_structure,
  traverse_recursive_backup,
)


def backup(origin: Path, target: Path) -> int:
  """Top-level backup logic.
  """
  logging.info("Backup started.")

  # First step is to iterate through target to trim those not in origin
  logging.debug("===== Cleaning folders in target not in origin")
  remove_target_outliers(target, origin)

  # Then ensure all folders in origin exist in target
  logging.debug("===== Mirror origin folder structure into target")
  reflect_directory_structure(origin, target)
  
  # Iterate through origin folders, indexing and backing up each
  traverse_recursive_backup(origin, target)

  logging.info("Backup completed.")
  return 0


def restore(origin: Path, target: Path) -> int:
  """Top-level restore logic.
  """
  logging.info("Restore started.")

  

  logging.info("Restore completed.")
  return 0


def main() -> int:
  """Standard entrypoint
  """
  try:
    args = parse_args()
    validate_origin_target(args.origin, args.target)

    logging.basicConfig(
      level=logging.DEBUG if args.verbose else logging.INFO,
      format='%(levelname)s: %(message)s'
    )

    logging.info(f"Origin: {args.origin.resolve()}")
    logging.info(f"Target: {args.target.resolve()}")

    # Clean target if enabled, ensure target exists
    if args.delete:
      logging.debug("===== Delete option active; nuking target.")
      clean_target(args.target)
    args.target.mkdir(parents=True, exist_ok=True)

    if args.restore:
      restore(args.origin, args.target)
    else:
      backup(args.origin, args.target)

  except Exception as e:
    # unexpected issues; extra logging for debugging
    logging.exception("Unexpected error")
    return 1

  return 0


if __name__ == "__main__":
  exit(main())
