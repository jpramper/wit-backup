# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

from pathlib import Path

from wit_backup.index import (
    create_index
)


class TestCreateIndex:
    """Tests for create_index function.
    """

    def test_creates_index_with_files(self, tmp_path: Path) -> None:
        pass

    def test_ignores_directories_and_symlinks(self) -> None:
        pass

    def test_creates_empty_index_empty_dir(self) -> None:
        pass

    def test_uses_md5(self) -> None:
        pass

    def test_same_content_same_hash(self) -> None:
        pass


class TestWriteIndex:
    """Tests for write_index function.
    """

    def test_writes_empty_file_when_index_empty(self) -> None:
        pass

    def test_writes_index_file(self) -> None:
        pass

    def test_overwrites_existing_index(self) -> None:
        pass

    def test_index_content_uses_correct_format(self) -> None:
        pass


class TestReadIndex:
    """Tests for read_index function.
    """

    def test_returns_empty_index_when_target_not_exists(self) -> None:
        pass

    def test_returns_empty_index_when_target_incorrect_name(self) -> None:
        pass

    def test_reads_valid_index(self) -> None:
        pass

    def test_strips_newlines(self) -> None:
        pass

    def test_returns_empty_index_when_target_wrong_content(self) -> None:
        pass


class TestIndexesMismatch:
    """Tests for indexes_mismatch function.
    """

    def test_return_true_when_target_index_not_exists(self) -> None:
        pass

    def test_return_true_when_origin_target_differ(self) -> None:
        pass

    def test_return_false_when_origin_target_match(self) -> None:
        pass
