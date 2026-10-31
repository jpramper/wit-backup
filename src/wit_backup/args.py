# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

""" Program arguments parsing and validation.
"""

from argparse import (
    ArgumentError,
    ArgumentParser,
    ArgumentTypeError,
    Namespace,
)
from pathlib import Path

from .constants import (
    LOG_FILE,
    TIMESTAMP_FILE,
    Mode,
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


def mode_arg (mode: str) -> Mode:
    """ Validation for optional mode argument. 

    Returns:
        Program mode, default BACKUP.
    """
    aliases = {
        'b': Mode.BACKUP,
        "backup": Mode.BACKUP,
        'r': Mode.RESTORE,
        "restore": Mode.RESTORE,
    }
    normalized = mode.lower()

    if normalized not in aliases:
        raise ArgumentTypeError(f"Mode must be 'b'/'backup' or 'r'/'restore' and is {mode}")

    return aliases[normalized]


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


def parse_args () -> Namespace:
    """ Command-line parser definitions for the module.
    """
    parser = ArgumentParser(
        description="Recursively zips and indexes every folder from origin into target.",
        usage="%(prog)s [opts] <origin> <target>"
    )

    # plain options
    parser.add_argument("-w", "--wary",
        help=(
            "Prevent backup if origin is empty and target is not. "
            "Prevent restore if target is not empty."
        ),
        action="store_true",
    )
    parser.add_argument("-l", "--log",
        help=(
            "Append log messages to a logfile at root of target. "
            f"Defaults to {LOG_FILE} if -L is not set."
        ),
        action="store_true",
    )
    parser.add_argument("-t", "--timestamp",
        help=f"Append start & finish time to a logfile ({TIMESTAMP_FILE}) at root of target.",
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
    parser.add_argument("-L", "--log-file", type=log_file,
        help="Specify a logfile path to save logs to.",
    )

    # mandatory arguments
    parser.add_argument("origin", type=origin_path, 
        help="Must be a directory. Parent folder to create a backup from.",
    )
    parser.add_argument("target", type=target_path,
        help="Must be a directory. Target folder to save backup files."
    )

    # optional arguments
    parser.add_argument("mode", type=mode_arg, default=Mode.BACKUP, nargs="?",
        help="[OPTIONAL] 'b'/'backup' for backup (default) or 'r'/'restore' for restore mode.",
    )

    args = parser.parse_args()

    # --log-file should also set --log 
    if args.log_file is not None:
        args.log = True

    return args
