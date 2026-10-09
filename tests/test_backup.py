# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

from pathlib import Path

from wit_backup.backup import (
    clean_target
)


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


class TestRemoveTargetOutliers:
    """Tests for remove_target_outliers function.
    """

    def removes_folders_not_in_origin(self) -> None:
        pass


class TestReflectDirectoryStructure:
    """Tests for reflect_directory_structure function.
    """

    def ignores_symlinks(self) -> None:
        pass


class TestZipContents:
    """Tests for zip_contents function.
    """

    def only_zips_files(self) -> None:
        pass


class TestTraverseRecursiveBackup:
    """Tests for traverse_recursive_backup function.
    """

    def creates_target_counterpart_if_not_exists(self) -> None:
        pass
