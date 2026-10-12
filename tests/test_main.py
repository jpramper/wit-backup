# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

from pathlib import Path
from shutil import rmtree

from wit_backup.main import (
    backup
)
from wit_backup.index import INDEX_FILE
from wit_backup.backup import BACKUP_FILE
from wit_backup.log import TIMESTAMP_FILE


class TestBackup:
    """ Tests for main backup function.
    """

    def test_basic_backup(
            self, 
            folder_struct_with_files: Path, 
            tmp_path: Path
            ) -> None:
        # perform first backup
        origin = folder_struct_with_files
        target = tmp_path / "target"

        backup(origin, target)

        assert (target / INDEX_FILE).exists()
        assert (target / BACKUP_FILE).exists()

    def test_returns_nonzero_when_wary_fullfills(
            self, 
            folder_struct_with_files: Path, 
            tmp_path: Path
            ) -> None:
        # perform first backup
        origin = folder_struct_with_files
        target = tmp_path / "target"

        backup(origin, target, wary=True)

        assert (target / INDEX_FILE).exists() # make sure first backup passed

        # nuke origin and try backup again
        for item in origin.iterdir():
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                rmtree(item)
        result = backup(origin, target, wary=True)

        assert result == 5 # ensure non-zero matching wary
        assert (target / INDEX_FILE).exists() # make sure first backup is still there

    def test_logs_timestamps_start_end_when_timestamp_active(
            self, 
            folder_struct_with_files: Path, 
            tmp_path: Path
            ) -> None:
        origin = folder_struct_with_files
        target = tmp_path / "target"

        backup(origin, target, timestamp=True)

        assert (target / TIMESTAMP_FILE).exists()
        with open((target / TIMESTAMP_FILE), "r") as l:
            content = l.read()

            assert "STARTED" in content
            assert "COMPLETED" in content
        

