# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

from pathlib import Path
from shutil import rmtree

from wit_backup.core import (
    wary_backup_check,
    wary_restore_check,
    clean_target,
    reflect_directory_structure,
    backup,
    restore,
)
from wit_backup.constants import (
    INDEX_FILE,
    BACKUP_FILE,
    TIMESTAMP_FILE,
)


class TestReflectDirectoryStructure:
    """ Tests for reflect_directory_structure function.
    """

    def test_creates_target_parent_if_not_exists(self, tmp_path: Path) -> None:
        origin = (tmp_path / "origin")
        (origin / "subfolder").mkdir(parents=True)
        target = (tmp_path / "target")

        reflect_directory_structure(origin, target)

        assert target.exists()

    def test_mirrors_folders_correctly(self, tmp_path: Path) -> None:
        origin = (tmp_path / "origin")
        (origin / "subfolder_a").mkdir(parents=True)
        (origin / "subfolder_b" / "nested").mkdir(parents=True)
        target = (tmp_path / "target")

        reflect_directory_structure(origin, target)

        assert (target / "subfolder_a").exists()
        assert (target / "subfolder_b" / "nested").exists()

    def test_ignores_symlinks(self, tmp_path: Path) -> None:
        origin = (tmp_path / "origin")
        (origin / "subfolder").mkdir(parents=True)
        (origin / "symlink").symlink_to(origin / "subfolder")
        target = (tmp_path / "target")

        reflect_directory_structure(origin, target)

        assert (origin / "symlink").exists()
        assert not (target / "symlink").exists()


class TestWaryBackupCheck:
    """ Tests for wary_backup_check function.
    """

    def test_returns_true_origin_empty_target_content(self, tmp_path: Path) -> None:
        origin = (tmp_path / "origin")
        target = (tmp_path / "target")
        origin.mkdir()
        target.mkdir()
        (target / "file_a.txt").write_text("content")

        assert wary_backup_check(origin, target) is True

    def test_returns_false_origin_content_target_content(self, tmp_path: Path) -> None:
        origin = (tmp_path / "origin")
        target = (tmp_path / "target")
        origin.mkdir()
        target.mkdir()
        (origin / "file_a.txt").write_text("content")
        (target / "file_b.txt").write_text("content")

        assert wary_backup_check(origin, target) is False

    def test_returns_false_origin_content_target_empty(self, tmp_path: Path) -> None:
        origin = (tmp_path / "origin")
        target = (tmp_path / "target")
        origin.mkdir()
        target.mkdir()
        (origin / "file_a.txt").write_text("content")

        assert wary_backup_check(origin, target) is False


class TestWaryRestpreCheck:
    """ Tests for wary_restore_check function.
    """

    def test_returns_true_target_content(self, tmp_path: Path) -> None:
        target = (tmp_path / "target")
        target.mkdir()
        (target / "file_a.txt").write_text("content")

        assert wary_restore_check(target) is True

    def test_returns_false_target_empty(self, tmp_path: Path) -> None:
        target = (tmp_path / "target")
        target.mkdir()

        assert wary_restore_check(target) is False


class TestCleanTarget:
    """ Tests for clean_target function.
    """

    def test_removes_files_in_target(self, tmp_path: Path) -> None:
        (tmp_path / "file1.txt").write_text("booyah")
        (tmp_path / "file2.txt").write_text("boom")

        clean_target(tmp_path)

        child_list = list(tmp_path.iterdir())
        assert len(child_list) == 0


    def test_removes_folders_in_target(self, tmp_path: Path) -> None:
        (tmp_path / "fakefolder").mkdir()

        clean_target(tmp_path)

        child_list = list(tmp_path.iterdir())
        assert len(child_list) == 0

    def test_does_nothing_when_target_not_exists(self, tmp_path: Path) -> None:
        target = tmp_path / "false_folder"
        
        clean_target(target)

    def test_removes_children_while_keeping_parent(self, tmp_path: Path) -> None:
        target = tmp_path / "parent"
        target.mkdir()
        (target / "filea.txt").write_text("content")
        (target / "subfolder").mkdir()

        clean_target(target)

        assert len(list(target.iterdir())) == 0
        assert target.exists()


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


class TestRestore:
    """ Tests for main restore function.
    """

    def test_basic_restore(
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

        pass
