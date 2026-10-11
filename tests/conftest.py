# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

import pytest
from pathlib import Path

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
    """ Adds files to the simple test folder tree. Note needs create_simple_test_folder_structure.
    """
    (folder_struct / "file_a.txt").write_text("file A")
    (folder_struct / "subfolder" / "file_b.txt").write_text("file B")

    return folder_struct