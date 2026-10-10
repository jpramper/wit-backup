# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

from pathlib import Path
from zipfile import ZipFile

from wit_backup.backup import (
    clean_target,
    remove_target_outliers,
    reflect_directory_structure,
    zip_contents,
    traverse_recursive_backup,
    BACKUP_FILE,
)
from wit_backup.index import INDEX_FILE


class TestCleanTarget:
    """Tests    for clean_target function.
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

class TestRemoveTargetOutliers:
    """Tests for remove_target_outliers function.
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


class TestReflectDirectoryStructure:
    """Tests for reflect_directory_structure function.
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


class TestZipContents:
    """Tests for zip_contents function.
    """

    def test_creates_target_folder_if_not_exists(self, tmp_path: Path) -> None:
        origin = (tmp_path / "origin")
        target = (tmp_path / "target")
        (origin / "subfolder").mkdir(parents=True)
        (origin / "file_a.txt").write_text("bang")

        zip_file = zip_contents(origin, target)

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

    def test_dies_nothing_if_origin_equals_target(self, tmp_path: Path) -> None:
        origin = (tmp_path / "origin")
        target = (tmp_path / "origin")
        (origin / "subfolder").mkdir(parents=True)
        (origin / "file_a.txt").write_text("bang")

        zip_contents(origin, target)

        assert len(list(target.iterdir())) == 2


class TestTraverseRecursiveBackup:
    """Tests for traverse_recursive_backup function.
    """

    def create_simple_test_folder_structure(self, dir: Path, parent_name: str) -> Path:
        """Helper to create a simple folder tree for unit tests to manipulate
        """
        work_dir = (dir / parent_name)
        (work_dir / "subfolder").mkdir(parents=True)
        (work_dir / "empty_subfolder").mkdir()
        return work_dir

    def populate_simple_test_folder_structure(self, dir: Path) -> None:
        """ Adds files to the simple test folder tree. Note needs create_simple_test_folder_structure.
        """
        (dir / "file_a.txt").write_text("file A")
        (dir / "subfolder" / "file_b.txt").write_text("file B")

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

    def test_correctly_creates_initial_backup(self, tmp_path: Path) -> None:
        origin = self.create_simple_test_folder_structure(tmp_path, "origin")
        self.populate_simple_test_folder_structure(origin)
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

    def test_does_nothing_if_no_changes(self, tmp_path: Path) -> None:
        """ 
        This should be a clone of test_correctly_creates_initial_backup
        except it runs traverse_recursive_backup twice
        """
        origin = self.create_simple_test_folder_structure(tmp_path, "origin")
        self.populate_simple_test_folder_structure(origin)
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

    def test_correctly_updates_existing_backup_new_files(self, tmp_path: Path) -> None:
        # perform first backup
        origin = self.create_simple_test_folder_structure(tmp_path, "origin")
        self.populate_simple_test_folder_structure(origin)
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

