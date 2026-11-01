# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

from pathlib import Path

from pytest import raises

from wit_backup.backup import traverse_recursive_backup
from wit_backup.restore import (
    traverse_recursive_restore,
    unzip_contents,
)


class TestUnzipContents:
    """ Tests for unzip_contents function.
    """

    def test_creates_target_folder_if_not_exists (self, tmp_path: Path) -> None:
        origin = (tmp_path / "origin")
        target = (tmp_path / "target")
        origin.mkdir(parents=True)
        (origin / "file_a.txt").write_text("bang")

        unzip_contents(origin, target)

        assert target.exists()

    def test_unzips_correctly (self, folder_with_zip_file: Path) -> None:
        target = folder_with_zip_file / "target"
        target.mkdir()

        unzip_contents(folder_with_zip_file / "asdf.zip", target)

        assert (target / "file_a.txt").exists()
        assert (target / "file_b.txt").exists()

    def test_overwrites_overlapping_preexisting_files (self, folder_with_zip_file: Path) -> None:
        target = folder_with_zip_file / "target"
        target.mkdir()

        test_file = target / "file_a.txt"
        test_file.write_text("CONTENT") # write content different from folder_with_zip_file

        unzip_contents(folder_with_zip_file / "asdf.zip", target)

        overwritten = test_file.read_text()

        assert "file A" in overwritten

    def test_does_nothing_not_zipfile (self, tmp_path: Path) -> None:
        unzip_contents(tmp_path / "UNEXISTANT.zip", tmp_path)

        assert len(list(tmp_path.iterdir())) == 0

    def test_unzips_encrypted_zip_with_password(self, folder_with_encrypted_zip_file: Path) -> None:
        target = folder_with_encrypted_zip_file / "target"
        target.mkdir()

        unzip_contents(folder_with_encrypted_zip_file / "secret.zip", target, password="secret")

        assert (target / "file_a.txt").read_text() == "file A"
        assert (target / "file_b.txt").read_text() == "file B"

    def test_raises_on_wrong_password(self, folder_with_encrypted_zip_file: Path) -> None:
        target = folder_with_encrypted_zip_file / "target"
        target.mkdir()

        with raises(RuntimeError):
            unzip_contents(folder_with_encrypted_zip_file / "secret.zip", target, password="wrong")


class TestTraverseRecursiveRestore:
    """ Tests for traverse_recursive_restore function.
    """

    def test_creates_target_counterpart_if_not_exists (self, tmp_path: Path) -> None:
        origin = (tmp_path / "origin")
        target = (tmp_path / "target")
        origin.mkdir()

        traverse_recursive_restore(origin, target)

        assert target.exists()
    
    def test_correctly_restores_empty_target (
            self, 
            folder_struct_with_files: Path, 
            tmp_path: Path
            ) -> None:
        origin = folder_struct_with_files
        target = tmp_path / "target"
        traverse_recursive_backup(origin, target)

        restore_target = tmp_path / "restore"
        traverse_recursive_restore(target, restore_target)

        assert (restore_target / "file_a.txt").exists()
        assert (restore_target / "subfolder" / "file_b.txt").exists()


    def test_overwrites_conflicting_files_in_target (
            self, 
            folder_struct_with_files: Path, 
            tmp_path: Path
            ) -> None:
        origin = folder_struct_with_files
        target = tmp_path / "target"
        traverse_recursive_backup(origin, target)

        restore_target = tmp_path / "restore"
        restore_target.mkdir()
        (restore_target / "file_a.txt").write_text("CONFLICT")
        traverse_recursive_restore(target, restore_target)

        assert "file A" in (restore_target / "file_a.txt").read_text()

    def test_correctly_restores_partial_tree (
            self, 
            folder_struct_with_files: Path, 
            tmp_path: Path
            ) -> None:
        origin = folder_struct_with_files
        target = tmp_path / "target"
        traverse_recursive_backup(origin, target)

        (origin / "file_a.txt").unlink()
        assert not (origin / "file_a.txt").exists()

        traverse_recursive_restore(target, origin)

        assert "file A" in (origin / "file_a.txt").read_text()

    def test_preserves_non_conflicting_files_in_target (
            self, 
            folder_struct_with_files: Path, 
            tmp_path: Path
            ) -> None:
        origin = folder_struct_with_files
        target = tmp_path / "target"
        traverse_recursive_backup(origin, target)

        restore_target = tmp_path / "restore"
        restore_target.mkdir()
        (restore_target / "file_c.txt").write_text("NON-CONFLICT")
        traverse_recursive_restore(target, restore_target)

        assert "NON-CONFLICT" in (restore_target / "file_c.txt").read_text()
        assert (restore_target / "subfolder").exists()

    def test_correctly_restores_encrypted_backup (
            self, 
            folder_struct_with_files: Path, 
            tmp_path: Path
            ) -> None:
        origin = folder_struct_with_files
        target = tmp_path / "target"
        traverse_recursive_backup(origin, target, password="secret")

        restore_target = tmp_path / "restore"
        traverse_recursive_restore(target, restore_target, password="secret")

        assert (restore_target / "file_a.txt").read_text() == "file A"
        assert (restore_target / "subfolder" / "file_b.txt").read_text() == "file B"
