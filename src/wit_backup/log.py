# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

from pathlib import Path
from datetime import datetime, timezone


TIMESTAMP_FILE = "wb-timestamps.log"


def log_timestamp (dest: Path, entry: str) -> datetime:
    """ Logs a timestamp onto the timestamp log with the received entry.
    """
    date_time = datetime.now(timezone.utc).replace(microsecond = 0)

    with open(dest / TIMESTAMP_FILE, "a") as ts:
        ts.write(f"Wit-Backup {entry} - " + str(date_time.replace()))

    return date_time
