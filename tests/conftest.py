# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

""" Custom fixtures for pytest unit tests.
"""

import pytest
from pathlib import Path
import zipfile


@pytest.fixture
def folder_struct (tmp_path: Path) -> Path:
    """Helper to create a simple folder tree for unit tests to manipulate
    """
    work_dir = (tmp_path / "parent")
    (work_dir / "subfolder").mkdir(parents=True)
    (work_dir / "empty_subfolder").mkdir()
    return work_dir


@pytest.fixture
def folder_struct_with_files (folder_struct: Path) -> Path:
    """ Adds files to the simple test folder tree. Note - needs create_simple_test_folder_structure.
    """
    (folder_struct / "file_a.txt").write_text("file A")
    (folder_struct / "subfolder" / "file_b.txt").write_text("file B")

    return folder_struct


@pytest.fixture
def folder_with_zip_file (tmp_path: Path) -> Path:
    """ Provides a zipfile with a file tree for testing.
    """
    file_a = tmp_path / "file_a.txt"
    file_b = tmp_path / "file_b.txt"
    file_a.write_text("file A")
    file_b.write_text("file B")

    zip_file = tmp_path / "asdf.zip"
    with zipfile.ZipFile(zip_file, mode="w", compression=zipfile.ZIP_DEFLATED) as zip:
        zip.write(file_a, arcname=file_a.name)
        zip.write(file_b, arcname=file_b.name)

    file_a.unlink()
    file_b.unlink()

    return tmp_path
