# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

from pathlib import Path
from shutil import rmtree
from zipfile import (
    ZIP_STORED,
    ZipFile,
)

from wit_backup.constants import (
    BACKUP_FILE,
    INDEX_FILE,
    TIMESTAMP_FILE,
    Mode,
)
from wit_backup.core import (
    backup,
    clean_target,
    find_backup_file,
    password_test,
    reflect_directory_structure,
    restore,
    wary_backup_check,
    wary_restore_check,
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


class TestFindBackupFile:
    """ Tests for find_backup_file function.
    """

    def test_returns_none_when_no_backup_file(self, tmp_path: Path) -> None:
        target = (tmp_path / "target")
        target.mkdir()
        (target / "file_a.txt").write_text("content")

        assert find_backup_file(target) is None

    def test_returns_none_when_target_does_not_exist(self, tmp_path: Path) -> None:
        target = (tmp_path / "target")

        assert find_backup_file(target) is None

    def test_returns_backup_file_in_root(self, tmp_path: Path) -> None:
        target = (tmp_path / "target")
        target.mkdir()
        (target / BACKUP_FILE).write_bytes(b"zipdata")

        assert find_backup_file(target) == (target / BACKUP_FILE)

    def test_returns_nested_backup_file(self, tmp_path: Path) -> None:
        target = (tmp_path / "target")
        (target / "subfolder" / "nested").mkdir(parents=True)
        (target / "subfolder" / "nested" / BACKUP_FILE).write_bytes(b"zipdata")

        assert find_backup_file(target) == (target / "subfolder" / "nested" / BACKUP_FILE)

    def test_ignores_symlinked_folders(self, tmp_path: Path) -> None:
        target = (tmp_path / "target")
        backup_store = (tmp_path / "backup_store")
        backup_store.mkdir()
        (backup_store / BACKUP_FILE).write_bytes(b"zipdata")
        target.mkdir()
        (target / "symlink").symlink_to(backup_store)

        assert find_backup_file(target) is None


class TestPasswordTest:
    """ Tests for password_test function.
    """

    def test_returns_true_when_no_backup_file_found(self, tmp_path: Path) -> None:
        target = (tmp_path / "target")
        target.mkdir()
        (target / "file_a.txt").write_text("content")

        assert password_test(Mode.BACKUP, target, None) is True

    def test_returns_true_when_no_backup_file_found_restore_mode(self, tmp_path: Path) -> None:
        target = (tmp_path / "target")
        target.mkdir()

        assert password_test(Mode.RESTORE, target, None) is True

    def test_returns_true_when_target_does_not_exist(self, tmp_path: Path) -> None:
        target = (tmp_path / "target")

        assert password_test(Mode.BACKUP, target, None) is True

    def test_returns_true_with_plain_backup_and_no_password(
            self,
            folder_struct_with_files: Path,
            tmp_path: Path
            ) -> None:
        origin = folder_struct_with_files
        target = tmp_path / "target"

        backup(origin, target)

        assert password_test(Mode.BACKUP, target, None) is True

    def test_returns_false_with_plain_backup_and_password(
            self,
            folder_struct_with_files: Path,
            tmp_path: Path
            ) -> None:
        # plain archives cannot be opened with a password
        origin = folder_struct_with_files
        target = tmp_path / "target"

        backup(origin, target)

        assert password_test(Mode.BACKUP, target, "anything") is False

    def test_returns_true_with_encrypted_backup_and_correct_password(
            self,
            folder_struct_with_files: Path,
            tmp_path: Path
            ) -> None:
        origin = folder_struct_with_files
        target = tmp_path / "target"

        backup(origin, target, password="secret")

        assert password_test(Mode.BACKUP, target, "secret") is True

    def test_returns_false_with_encrypted_backup_and_no_password(
            self,
            folder_struct_with_files: Path,
            tmp_path: Path
            ) -> None:
        origin = folder_struct_with_files
        target = tmp_path / "target"

        backup(origin, target, password="secret")

        assert password_test(Mode.BACKUP, target, None) is False

    def test_returns_false_with_encrypted_backup_and_wrong_password(
            self,
            folder_struct_with_files: Path,
            tmp_path: Path
            ) -> None:
        origin = folder_struct_with_files
        target = tmp_path / "target"

        backup(origin, target, password="secret")

        assert password_test(Mode.BACKUP, target, "wrong") is False

    def test_returns_false_when_backup_file_corrupted(self, tmp_path: Path) -> None:
        # craft a backup file whose content no longer matches its CRC
        target = (tmp_path / "target")
        target.mkdir()
        zip_file = (target / BACKUP_FILE)
        with ZipFile(zip_file, "w", compression=ZIP_STORED) as zf:
            zf.writestr("file_a.txt", "file A")
        with open(zip_file, "r+b") as f:
            # flip one byte of the stored content
            f.seek(40)
            f.write(b"X")

        assert password_test(Mode.BACKUP, target, "secret") is False

    def test_returns_false_in_restore_mode_with_wrong_password(
            self,
            folder_struct_with_files: Path,
            tmp_path: Path
            ) -> None:
        origin = folder_struct_with_files
        target = tmp_path / "target"

        backup(origin, target, password="secret")

        assert password_test(Mode.RESTORE, target, "wrong") is False

    def test_returns_true_when_only_nested_backup_exists(
            self,
            folder_struct: Path,
            tmp_path: Path
            ) -> None:
        # only subfolder has files, so only subfolder gets a backup file
        origin = folder_struct
        (origin / "subfolder" / "file_b.txt").write_text("file B")
        target = tmp_path / "target"

        backup(origin, target, password="secret")

        assert password_test(Mode.BACKUP, target, "secret") is True
        assert password_test(Mode.BACKUP, target, "wrong") is False


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
        with open(target / TIMESTAMP_FILE) as log_file:
            content = log_file.read()

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

        restore_target = tmp_path / "restore"

        restore(target, restore_target)

        assert (restore_target / "file_a.txt").exists()
        assert (restore_target / "subfolder" / "file_b.txt").exists()
        assert (restore_target / "subfolder").is_dir()

    def test_basic_restore_with_password(
            self, 
            folder_struct_with_files: Path, 
            tmp_path: Path
            ) -> None:
        # perform first backup with password
        origin = folder_struct_with_files
        target = tmp_path / "target"

        backup(origin, target, password="secret")

        restore_target = tmp_path / "restore"

        restore(target, restore_target, password="secret")

        assert (restore_target / "file_a.txt").read_text() == "file A"
        assert (restore_target / "subfolder" / "file_b.txt").read_text() == "file B"

    def test_returns_nonzero_when_wary_fullfills(
            self, 
            folder_struct_with_files: Path, 
            tmp_path: Path
            ) -> None:
        origin = folder_struct_with_files
        target = tmp_path / "target"

        backup(origin, target) # create a basic backup

        restore_target = tmp_path / "restore"
        restore_target.mkdir()
        (restore_target / "in_the_way.txt").write_text("content")

        result = restore(target, restore_target, wary=True)

        assert result == 6 # ensure non-zero matching wary
        assert not (restore_target / "file_a.txt").exists()

    def test_logs_timestamps_start_end_when_timestamp_active(
            self, 
            folder_struct_with_files: Path, 
            tmp_path: Path
            ) -> None:
        origin = folder_struct_with_files
        target = tmp_path / "target"

        backup(origin, target)

        restore_target = tmp_path / "restore"

        restore(target, restore_target, timestamp=True)

        assert (restore_target / TIMESTAMP_FILE).exists()
        with open(restore_target / TIMESTAMP_FILE) as log_file:
            content = log_file.read()

            assert "STARTED" in content
            assert "COMPLETED" in content
