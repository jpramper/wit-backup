# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
from sys import stdout


TIMESTAMP_FILE = "wb-timestamps.log"


def configure_logging (
        verbose: bool = False, 
        quiet: bool = False,
        log_file: Optional[Path] = None,
        ) -> None: # pragma: no cover
    log_level = logging.INFO
    if verbose:
        logging.DEBUG
    if quiet:
        logging.ERROR

    handler = logging.StreamHandler(stdout)
    if log_file is not None:
        handler = logging.FileHandler(log_file, mode="a")

    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(message)s',
        handlers=[handler]
    )


def log_timestamp (dest: Path, entry: str) -> datetime:
    """ Logs a timestamp onto the timestamp log with the received entry.
    """
    date_time = datetime.now(timezone.utc).replace(microsecond = 0)

    with open(dest / TIMESTAMP_FILE, "a") as ts:
        ts.write(f"Wit-Backup {entry} - " + str(date_time.replace()) + "\n")

    return date_time
