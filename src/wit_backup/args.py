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
    """ Validation for origin folder argument.
    """
    p = Path(path)

    if not p.exists():
        raise FileNotFoundError(f"'{path}' does not exist")
    
    if not p.is_dir():
        raise NotADirectoryError(f"'{path}' is not a directory")
    return p


def target_path (path: str) -> Path:
    """ Validation for target folder argument.
    """
    p = Path(path)
    
    if p.exists() and not p.is_dir():
        raise ArgumentError(None, f"'{path}' as target exists and is not a folder")
    return p


def log_file (file: str) -> Path:
    """ Validation for logfile argument.
    """
    f = Path(file)

    if f.exists() and not f.is_file():
        raise ArgumentError(None, "Specified logfile exists and is not a writable file.")

    return f


def validate_origin_target (origin: Path, target: Path) -> None:
    """ Validation for both origin & target.
    """
    if origin.resolve() == target.resolve():
        raise ArgumentError(None, "Origin and Target are the same folder")


def wary_backup_check (origin: Path, target: Path) -> bool:
    """ 
    Validates if origin is empty and target is not, returns true if so.
    This is important in vase of a main drive failure, so a backup doesnt falsely
    clean a recurrent target backup to match a currently-empty origin.
    """
    if len(list(origin.iterdir())) == 0 and len(list(target.iterdir())) != 0:
        return True

    return False


def parse_args () -> Namespace:
    """ Command-line parser definitions for the module.
    """
    parser = ArgumentParser(
        description="Recursively zips and indexes every folder from origin into target.",
        usage="%(prog)s [opts] <origin> <target>"
    )

    # plain options
    parser.add_argument("-w", "--wary",
        help="Prevent backup if origin is empty and target is not.",
        action="store_true",
    )
    parser.add_argument("-t", "--timestamp",
        help="Append start & finish time to a logfile at root of target.",
        action="store_true",
    )
    parser.add_argument("-r", "--restore",
        help="Perform a restoration instead of backup. Unpacks zips from <origin>'s tree into <target>'s respective folders.",
        action="store_true",
    )
    parser.add_argument("-d", "--delete",
        help="Clean target folder before starting operations. CAUTION: recursive.",
        action="store_true"
    )
    parser.add_argument("-v", "--verbose",
        help="Print extra diagnostic info.",
        action="store_true",
    )
    parser.add_argument("-q", "--quiet",
        help="Only print error messages.",
        action="store_true",
    )

    # options with arguments
    parser.add_argument("-l", "--logfile", type=log_file,
        help="Prevent backup if origin is empty and target is not.",
    )

    # mandatory arguments
    parser.add_argument("origin", type=origin_path, 
        help="Must be a directory. Parent folder to create a backup from.",
    )
    parser.add_argument("target", type=target_path,
        help="Must be a directory. Target folder to save backup files."
    )

    return parser.parse_args()
