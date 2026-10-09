# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

from pytest import raises
from pathlib import Path
from argparse import ArgumentError
import sys

from wit_backup.args import (
    origin_path,
    target_path,
    validate_origin_target,
    parse_args,
)


class TestOriginPath: 
    """Tests for origin_path function.
    """

    def test_returns_path_for_existing_directory(self, tmp_path: Path) -> None:
        mock_dir = (tmp_path / "mock_dir")
        mock_dir.mkdir()
        
        assert isinstance(origin_path(str(mock_dir)), Path)

    def test_raises_when_origin_not_exists(self, tmp_path: Path) -> None:
        mock_dir = (tmp_path / "false_dir")

        with raises(FileNotFoundError) as exc_info:
            origin_path(str(mock_dir))

        assert "does not exist" in (str(exc_info.value))

    def test_raises_when_origin_not_directory(self, tmp_path: Path) -> None:
        mock_file = (tmp_path / "mock_file.txt")
        mock_file.write_text("content")

        with raises(NotADirectoryError) as exc_info:
            origin_path(str(mock_file))

        assert "is not a directory" in (str(exc_info.value))


class TestTargetPath:
    """Tests for target_path function.
    """

    def test_returns_path_for_existing_directory(self, tmp_path: Path) -> None:
        mock_dir = (tmp_path / "mock_dir")
        mock_dir.mkdir()

        assert isinstance(target_path(str(mock_dir)), Path)

    def test_returns_path_for_nonexisting_target(self, tmp_path: Path) -> None:
        mock_dir = (tmp_path / "false_dir")
        
        assert isinstance(target_path(str(mock_dir)), Path)

    def test_fails_when_target_exists_as_file(self, tmp_path: Path) -> None:
        mock_file = (tmp_path / "mock_file.txt")
        mock_file.write_text("content")

        with raises(ArgumentError) as exc_info:
            target_path(str(mock_file))

        assert "target exists and is not a folder" in (str(exc_info.value))


class TestValidateOriginTarget:
    """Tests for validate_origin_target function.
    """

    def test_raises_when_origin_target_are_equal(self, tmp_path: Path) -> None:
        origin = (tmp_path / "folder_a")
        target = (tmp_path / "folder_a")

        with raises(ArgumentError) as exc_info:
            validate_origin_target(origin, target)

        assert "Origin and Target are the same folder" in str(exc_info)

    def test_does_noting_when_origin_target_are_different(self, tmp_path: Path) -> None:
        origin = (tmp_path / "folder_a")
        target = (tmp_path / "folder_b")

        validate_origin_target(origin, target)


class TestParseArgs:
    """Tests for parse_args function.
    """

    def test_restore_default_false(self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", origin, target]

            result = parse_args()

            assert result.restore is False
        finally:
            sys.argv = original_argv

    def test_delete_default_false(self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", origin, target]

            result = parse_args()

            assert result.delete is False
        finally:
            sys.argv = original_argv

    def test_verbose_default_false(self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", origin, target]

            result = parse_args()

            assert result.verbose is False
        finally:
            sys.argv = original_argv

    def test_allows_setting_up_restore(self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", "-r", origin, target]

            result = parse_args()

            assert result.restore is True
        finally:
            sys.argv = original_argv

    def test_allows_setting_up_delete(self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", "-d", origin, target]

            result = parse_args()

            assert result.delete is True
        finally:
            sys.argv = original_argv

    def test_allows_setting_up_verbose(self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", "-v", origin, target]

            result = parse_args()

            assert result.verbose is True
        finally:
            sys.argv = original_argv

    def test_defines_origin_target_as_paths(self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", "-r", origin, target]

            result = parse_args()

            assert isinstance(result.origin, Path)
            assert isinstance(result.target, Path)
        finally:
            sys.argv = original_argv