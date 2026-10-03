#!/usr/bin/env python3

# Copyright Juan Pablo Ramirez 2026

import logging

from .args import parse_args
from .backup import (
  clean_target,
  remove_target_outliers,
  reflect_directory_structure,
  traverse_recursive_backup,
)


def main() -> int:
  try:
    args = parse_args()

    logging.basicConfig(
      level=logging.DEBUG if args.verbose else logging.INFO,
      format='%(levelname)s: %(message)s'
    )
    logging.info("Backup Started.")

    origin = args.origin
    target = args.target
    logging.info(f"Origin: {origin.resolve()}")
    logging.info(f"Target: {target.resolve()}")

    # Clean target if enabled, ensure target exists
    if args.delete:
      logging.debug("===== Delete option active; nuking target.")
      clean_target(args.target)
    target.mkdir(parents=True, exist_ok=True)

    # First step is to iterate through target to trim those not in origin
    logging.debug("===== Cleaning folders in target not in origin")
    remove_target_outliers(target, origin)

    # Then ensure all folders in origin exist in target
    logging.debug("===== Mirror origin folder structure into target")
    reflect_directory_structure(origin, target)
    
    # Iterate through origin folders, indexing and backing up each
    traverse_recursive_backup(origin, target)

    logging.info("Completed backup.")

  except Exception as e:
    # unexpected issues; extra logging for debugging
    logging.exception("Unexpected error")
    return 1

  return 0


if __name__ == "__main__":
  exit(main())