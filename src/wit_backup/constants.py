# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

""" Package constants.
"""

from enum import StrEnum

BACKUP_FILE: str = "_backup_.zip"
""" Filename for backup files. Note if this changes, restores of backups made before the change 
will fail to find the backup zip.
"""


INDEX_FILE: str = "_index_"
""" Filename for index files. Note if this changes, backups made before the change with a 
different filename will fail to find previous indexes and will re-backup everything.
"""


TIMESTAMP_FILE: str = "wb-timestamps.log"
""" timestamp log file filename for option -t """


LOG_FILE: str = "wb-runtime.log"
""" default logfile for -l unless overridden by -L """


class Mode (StrEnum):
    """ Program operation modes. """

    BACKUP = "backup"
    
    RESTORE = "restore"
