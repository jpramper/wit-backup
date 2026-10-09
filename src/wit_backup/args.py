# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

# Program arguments parsing and validation.

from pathlib import Path
from argparse import (
  ArgumentError, 
  Namespace, 
  ArgumentParser,
)


def origin_path (path: str) -> Path:
  """Validation for origin folder argument.
  """
  p = Path(path)

  if not p.exists():
    raise FileNotFoundError(f"'{path}' does not exist")
  
  if not p.is_dir():
    raise NotADirectoryError(f"'{path}' is not a directory")
  return p


def target_path (path: str) -> Path:
  """Validation for target folder argument.
  """
  p = Path(path)
  
  if p.exists() and not p.is_dir():
    raise ArgumentError(None, f"'{path}' as target exists and is not a folder")
  return p


def validate_origin_target (origin: Path, target: Path) -> None:
  """Validation for both origin & target.
  """
  if origin.resolve() == target.resolve():
    raise ArgumentError(None, "Origin and Target are the same folder")


def parse_args () -> Namespace:
  """Command-line parser definitions for the module.
  """
  parser = ArgumentParser(
    description="Recursively zips and indexes every folder from origin into target.",
    usage="%(prog)s [opts] <origin> <target>"
  )

  # options
  parser.add_argument("-r", "--restore",
    help="Perform a restoration instead of backup. Unpacks zips from <origin>'s tree into <target>'s respective folders.",
    action="store_true",
  )
  parser.add_argument("-d", "--delete",
    help="Clean target folder before starting backup.",
    action="store_true"
  )
  parser.add_argument("-v", "--verbose",
    help="Print extra diagnostic info.",
    action="store_true",
  )

  # mandatory paths
  parser.add_argument("origin", type=origin_path, 
    help="Must be a directory. Parent folder to create a backup from.",
  )
  parser.add_argument("target", type=target_path,
    help="Must be a directory. Target folder to save backup files."
  )

  return parser.parse_args()
