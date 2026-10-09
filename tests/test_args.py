# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

from pathlib import Path

from wit_backup.args import (
    origin_path
)


class TestOriginPath: 
    """Tests for origin_path function.
    """

    def returns_path_for_existing_directory(self) -> None:
        pass

    def test_raises_when_origin_not_exists(self) -> None:
        pass

    def test_raises_when_origin_not_directory(self) -> None:
        pass


class TestTargetPath:
    """Tests for target_path function.
    """

    def returns_path_for_existing_directory(self) -> None:
        pass

    def returns_path_for_nonexisting_target(self) -> None:
        pass

    def test_fails_when_target_exists_as_file(self) -> None:
        pass


class TestValidateOriginTarget:
    """Tests for validate_origin_target fucntion.
    """

    def test_raises_when_origin_and_target_are_equal(self) -> None:
        pass


class TestParseArgs:
    """Tests for parse_args function.
    """

    def test_verbose_default_false(self) -> None:
        pass

    def test_allows_setting_up_restore(self) -> None:
        pass

    def test_allows_setting_up_verbose(self) -> None:
        pass

    def test_allows_setting_up_delete(self) -> None:
        pass

    def test_defines_origin_target_as_paths(self) -> None:
        pass