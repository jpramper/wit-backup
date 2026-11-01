# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

from pathlib import Path
from zipfile import ZipFile

import pyzipper
from pytest import raises

from wit_backup.backup import (
    remove_target_outliers,
    traverse_recursive_backup,
    zip_contents,
)
from wit_backup.constants import (
    BACKUP_FILE,
    INDEX_FILE,
)


class TestRemoveTargetOutliers:
    """ Tests for remove_target_outliers function.
    """

    def create_simple_test_folder_structure(self, dir: Path, parent_name: str) -> Path:
        """Helper to create a simple folder structure for unit tests to manipulate
        """
        origin = (dir / parent_name)
        (origin / "subfolder").mkdir(parents=True)
        (origin / "file_a.txt").write_text("file A")
        (origin / "subfolder" / "file_b.txt").write_text("file B")
        return origin

    def test_removes_folders_not_in_origin(self, tmp_path: Path) -> None:
        origin = self.create_simple_test_folder_structure(tmp_path, "origin")
        target = self.create_simple_test_folder_structure(tmp_path, "target")
        (target / "subfolder" / "false_1").mkdir()
        (target  / "false_2").mkdir()

        remove_target_outliers(target, origin)

        assert not (target / "false_2").exists()
        assert not (target / "subfolder" / "false_1").exists()

    def test_ignores_files(self, tmp_path: Path) -> None:
        origin = self.create_simple_test_folder_structure(tmp_path, "origin")
        target = self.create_simple_test_folder_structure(tmp_path, "target")
        file_1 = (target / "subfolder" / "extra_file_1.txt")
        file_1.write_text("asdf")
        file_2 = (target  / "extra_file_2.txt")
        file_2.write_text("qwer")

        remove_target_outliers(target, origin)

        assert file_1.exists()
        assert file_2.exists()

    def test_removes_symlinks_not_in_origin(self, tmp_path: Path) -> None:
        origin = self.create_simple_test_folder_structure(tmp_path, "origin")
        target = self.create_simple_test_folder_structure(tmp_path, "target")
        false_folder = (target / "subfolder" / "false_1")
        false_folder.mkdir()
        (target  / "symlink_1").symlink_to(false_folder)

        assert (target  / "symlink_1").exists()
        assert (target  / "symlink_1").is_symlink()

        remove_target_outliers(target, origin)

        assert not (target / "symlink_1").exists()


class TestZipContents:
    """ Tests for zip_contents function.
    """

    def test_creates_target_folder_if_not_exists(self, tmp_path: Path) -> None:
        origin = (tmp_path / "origin")
        target = (tmp_path / "target")
        (origin / "subfolder").mkdir(parents=True)
        (origin / "file_a.txt").write_text("bang")

        zip_contents(origin, target)

        assert target.exists()

    def test_zips_files(self, tmp_path: Path) -> None:
        origin = (tmp_path / "origin")
        target = (tmp_path / "target")
        target.mkdir()
        (origin / "subfolder").mkdir(parents=True)
        (origin / "file_a.txt").write_text("bang")

        zip_file = zip_contents(origin, target)

        with ZipFile(zip_file, mode="r") as zf:
            names = zf.namelist()
            assert "file_a.txt" in names

    def test_zips_files_encrypted_with_password(self, tmp_path: Path) -> None:
        origin = (tmp_path / "origin")
        target = (tmp_path / "target")
        origin.mkdir()
        target.mkdir()
        (origin / "file_a.txt").write_text("bang")

        zip_file = zip_contents(origin, target, password="secret")

        with pyzipper.AESZipFile(zip_file, mode="r") as zf:
            zf.setpassword(b"secret")
            assert zf.read("file_a.txt") == b"bang"

    def test_encrypted_zip_not_readable_without_password(self, tmp_path: Path) -> None:
        origin = (tmp_path / "origin")
        target = (tmp_path / "target")
        origin.mkdir()
        target.mkdir()
        (origin / "file_a.txt").write_text("bang")

        zip_file = zip_contents(origin, target, password="secret")

        with raises(RuntimeError):
            with ZipFile(zip_file, mode="r") as zf:
                zf.read("file_a.txt")

    def test_ignores_directories(self, tmp_path: Path) -> None:
        origin = (tmp_path / "origin")
        target = (tmp_path / "target")
        target.mkdir()
        (origin / "subfolder").mkdir(parents=True)
        (origin / "file_a.txt").write_text("bang")

        zip_file = zip_contents(origin, target)

        with ZipFile(zip_file, mode="r") as zf:
            names = zf.namelist()
            assert "subfolder" not in names

    def test_does_nothing_if_no_files(self, tmp_path: Path) -> None:
        origin = (tmp_path / "origin")
        target = (tmp_path / "target")
        origin.mkdir()
        target.mkdir()

        zip_contents(origin, target)

        assert len(list(target.iterdir())) == 0

    def test_does_nothing_if_origin_equals_target (self, tmp_path: Path) -> None:
        origin = (tmp_path / "origin")
        target = (tmp_path / "origin")
        (origin / "subfolder").mkdir(parents=True)
        (origin / "file_a.txt").write_text("bang")

        zip_contents(origin, target)

        assert len(list(target.iterdir())) == 2


class TestTraverseRecursiveBackup:
    """ Tests for traverse_recursive_backup function.
    """

    def test_creates_target_counterpart_if_not_exists(self, tmp_path: Path) -> None:
        origin = (tmp_path / "origin")
        target = (tmp_path / "target")
        origin.mkdir()

        traverse_recursive_backup(origin, target)

        assert target.exists()

    def test_does_nothing_if_origin_empty(self, tmp_path: Path) -> None:
        origin = (tmp_path / "origin")
        target = (tmp_path / "target")
        origin.mkdir()

        traverse_recursive_backup(origin, target)

        assert len(list(target.iterdir()))

    def test_correctly_creates_initial_backup(
            self, 
            folder_struct_with_files: Path, 
            tmp_path: Path
            ) -> None:
        origin = folder_struct_with_files
        target = tmp_path / "target"

        traverse_recursive_backup(origin, target)

        assert (target / "subfolder").exists()
        assert (target / "empty_subfolder").exists()

        assert (target / INDEX_FILE).exists()
        assert (target / "subfolder" / INDEX_FILE).exists()

        assert "file_a.txt" in (target / INDEX_FILE).read_text()
        assert "file_b.txt" in (target / "subfolder" / INDEX_FILE).read_text()

        assert (target / BACKUP_FILE).exists()
        assert (target / "subfolder" / BACKUP_FILE).exists()

        with ZipFile((target / BACKUP_FILE), mode="r") as zf:
            names = zf.namelist()
            assert "file_a.txt" in names
        with ZipFile((target / "subfolder" / BACKUP_FILE), mode="r") as zf:
            names = zf.namelist()
            assert "file_b.txt" in names

    def test_does_nothing_if_no_changes(
            self, 
            folder_struct_with_files: Path, 
            tmp_path: Path
            ) -> None:
        """ 
        This should be a clone of test_correctly_creates_initial_backup
        except it runs traverse_recursive_backup twice
        """
        origin = folder_struct_with_files
        target = tmp_path / "target"

        traverse_recursive_backup(origin, target)
        # run twice, second time with no changes
        traverse_recursive_backup(origin, target)

        assert (target / "subfolder").exists()
        assert (target / "empty_subfolder").exists()

        assert (target / INDEX_FILE).exists()
        assert (target / "subfolder" / INDEX_FILE).exists()

        assert "file_a.txt" in (target / INDEX_FILE).read_text()
        assert "file_b.txt" in (target / "subfolder" / INDEX_FILE).read_text()

        assert (target / BACKUP_FILE).exists()
        assert (target / "subfolder" / BACKUP_FILE).exists()

        with ZipFile((target / BACKUP_FILE), mode="r") as zf:
            names = zf.namelist()
            assert "file_a.txt" in names
        with ZipFile((target / "subfolder" / BACKUP_FILE), mode="r") as zf:
            names = zf.namelist()
            assert "file_b.txt" in names

    def test_correctly_updates_existing_backup_new_files(
            self, 
            folder_struct_with_files: Path, 
            tmp_path: Path
            ) -> None:
        # perform first backup
        origin = folder_struct_with_files
        target = tmp_path / "target"

        traverse_recursive_backup(origin, target)

        # add a file, and backup again
        (origin / "file_c.txt").write_text("content")

        traverse_recursive_backup(origin, target)

        assert "file_a.txt" in (target / INDEX_FILE).read_text()
        assert "file_c.txt" in (target / INDEX_FILE).read_text()

        with ZipFile((target / BACKUP_FILE), mode="r") as zf:
            names = zf.namelist()
            assert "file_a.txt" in names
            assert "file_c.txt" in names

    def test_correctly_creates_encrypted_backup(
            self, 
            folder_struct_with_files: Path, 
            tmp_path: Path
            ) -> None:
        origin = folder_struct_with_files
        target = tmp_path / "target"

        traverse_recursive_backup(origin, target, password="secret")

        assert (target / BACKUP_FILE).exists()
        assert (target / "subfolder" / BACKUP_FILE).exists()

        with pyzipper.AESZipFile((target / BACKUP_FILE), mode="r") as zf:
            zf.setpassword(b"secret")
            assert "file_a.txt" in zf.namelist()
        with pyzipper.AESZipFile((target / "subfolder" / BACKUP_FILE), mode="r") as zf:
            zf.setpassword(b"secret")
            assert "file_b.txt" in zf.namelist()
