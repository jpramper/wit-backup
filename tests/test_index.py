# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

from pathlib import Path
from pytest import raises

from wit_backup.index import (
    create_index,
    write_index,
    read_index,
    indexes_mismatch,
)
from wit_backup.constants import INDEX_FILE


class TestCreateIndex:
    """ Tests for create_index function.
    """

    def test_creates_index_with_files(self, tmp_path: Path) -> None:
        (tmp_path / "file_a.txt").write_text("Oh boy!")
        (tmp_path / "file_b.txt").write_text("content")
        
        index = create_index(tmp_path)

        assert len(index) == 2
        assert "file_a.txt" in index
        assert "file_b.txt" in index
        assert isinstance(index["file_a.txt"], str)
        assert isinstance(index["file_b.txt"], str)
        assert index["file_a.txt"] != index["file_b.txt"]

    def test_creates_index_with_md5_hashes(self, tmp_path: Path) -> None:
        (tmp_path / "file_a.txt").write_text("jumping")
        (tmp_path / "file_b.txt").write_text("content")
        
        index = create_index(tmp_path)

        assert len(index["file_a.txt"]) == 32
        assert len(index["file_b.txt"]) == 32

    def test_ignores_directories_and_symlinks(self, tmp_path: Path) -> None:
        (tmp_path / "file_a.txt").write_text("content")
        (tmp_path / "directory").mkdir()
        (tmp_path / "symlink").symlink_to((tmp_path / "directory"))
        
        index = create_index(tmp_path)

        assert "file_a.txt" in index
        assert "directory" not in index
        assert "symlink" not in index

    def test_creates_empty_index_empty_dir(self, tmp_path: Path) -> None:
        index = create_index(tmp_path)

        assert len(index) == 0

    def test_same_content_same_hash(self, tmp_path: Path) -> None:
        (tmp_path / "file_a.txt").write_text("content")
        (tmp_path / "file_b.txt").write_text("content")
        
        index = create_index(tmp_path)

        assert len(index) == 2
        assert index["file_a.txt"] == index["file_b.txt"]


class TestWriteIndex:
    """ Tests for write_index function.
    """

    def test_writes_empty_file_when_index_empty(self, tmp_path: Path) -> None:
        index_file = write_index(dict(), tmp_path)

        assert index_file.exists() and index_file.is_file()
        assert index_file.stat().st_size == 0

    def test_writes_index_file(self, tmp_path: Path) -> None:
        index = {"asdf.txt": "f47t2upk"}
        index_file = write_index(index, tmp_path)
        
        assert index_file.exists() and index_file.is_file()
        assert index_file.stat().st_size != 0

    def test_overwrites_existing_index(self, tmp_path: Path) -> None:
        (tmp_path / INDEX_FILE).write_text("content")
        index = {"asdf.txt": "f47t2upk"}
        index_file = write_index(index, tmp_path)

        written_index = index_file.read_text()
        assert "content" not in written_index
        assert "asdf.txt/f47t2upk" in written_index

    def test_index_content_uses_correct_format(self, tmp_path: Path) -> None:
        index = {"asdf.txt": "f47t2upk"}
        index_file = write_index(index, tmp_path)
        
        assert "asdf.txt/f47t2upk" in index_file.read_text()


class TestReadIndex:
    """ Tests for read_index function.
    """

    def test_raises_when_index_not_file(self, tmp_path: Path) -> None:
        index_file = tmp_path / INDEX_FILE
        index_file.mkdir()

        with raises(IsADirectoryError) as exc_info:
          read_index(index_file)

        assert "is not a file" in str(exc_info.value)

    def test_returns_empty_index_when_target_not_exists(self, tmp_path: Path) -> None:
        index_file = tmp_path / INDEX_FILE

        result = read_index(index_file)

        assert result == dict()

    def test_returns_empty_index_when_target_incorrect_name(self, tmp_path: Path) -> None:
        index_file = tmp_path / "asdf.txt"
        index_file.write_text("qwer.txt/12345678")
        
        result = read_index(index_file)

        assert result == dict()

    def test_reads_valid_index(self, tmp_path: Path) -> None:
        index_file = tmp_path / INDEX_FILE
        index_file.write_text("qwer.txt/12345678")

        result = read_index(index_file)

        assert result == {"qwer.txt": "12345678"}

    def test_strips_newlines(self, tmp_path: Path) -> None:
        index_file = tmp_path / INDEX_FILE
        index_file.write_text("qwer.txt/12345678\n")

        result = read_index(index_file)

        assert result == {"qwer.txt": "12345678"}

    def test_returns_empty_index_when_target_wrong_content(self, tmp_path: Path) -> None:
        index_file = tmp_path / INDEX_FILE
        index_file.write_text("a/s/d/f")
        
        result = read_index(index_file)

        assert result == dict()

    def test_returns_empty_index_when_unable_open(self, tmp_path: Path) -> None:
        index_file = tmp_path / INDEX_FILE
        index_file.write_text("qwer.txt/12345678\n")
        
        # remove read permission to trigger exception:
        index_file.chmod(0o200)
        
        result = read_index(index_file)

        assert result == dict()


class TestIndexesMismatch:
    """ Tests for indexes_mismatch function.
    """
    
    def test_return_true_when_origin_target_differ(self, tmp_path: Path) -> None:
        origin_index = {"asdf.txt": "f47t2upk"}
        target_index = (tmp_path / INDEX_FILE)
        target_index.write_text("qwer.txt/b89q3l01")

        assert indexes_mismatch(origin_index, tmp_path)

    def test_return_true_when_target_index_not_exists(self, tmp_path: Path) -> None:
        origin_index = {"qwer.txt": "mb91l47f"}

        assert indexes_mismatch(origin_index, tmp_path)

    def test_return_false_when_origin_target_match(self, tmp_path: Path) -> None:
        origin_index = {"asdf.txt": "f47t2upk"}
        target_index = (tmp_path / INDEX_FILE)
        target_index.write_text("asdf.txt/f47t2upk")
        print(indexes_mismatch(origin_index, tmp_path))

        assert indexes_mismatch(origin_index, tmp_path) is False
