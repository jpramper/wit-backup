# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

import sys
from argparse import (
    ArgumentError,
    ArgumentTypeError,
)
from pathlib import Path

from pytest import raises

from wit_backup.args import (
    log_file,
    mode_arg,
    origin_path,
    parse_args,
    target_path,
    validate_origin_target,
    validate_password,
)
from wit_backup.constants import (
    PASS_ENV_VAR,
    PASSFILE_ENV_VAR,
    Mode,
)


class TestOriginPath: 
    """ Tests for origin_path function.
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
    """ Tests for target_path function.
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


class TestLogFile:
    """ Tests for log_file function.
    """

    def test_returns_path_for_nonexisting_file(self, tmp_path: Path) -> None:
        mock_log = (tmp_path / "log.txt")

        assert isinstance(log_file(str(mock_log)), Path)

    def test_returns_path_for_existing_file(self, tmp_path: Path) -> None:
        mock_log = (tmp_path / "log.txt")
        mock_log.write_text("content")

        assert isinstance(log_file(str(mock_log)), Path)

    def test_raises_when_target_is_directory(self, tmp_path: Path) -> None:
        mock_log = (tmp_path / "log.txt")
        mock_log.mkdir()

        with raises(ArgumentError) as exc_info:
            log_file(str(mock_log))
        
        assert "logfile exists and is not a writable file" in str(exc_info.value)


class TestValidateOriginTarget:
    """ Tests for validate_origin_target function.
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


class TestValidatePassword:
    """ Tests for validate_password function.
    """

    def test_raises_when_password_enabled_and_no_env_set(self, monkeypatch) -> None:
        monkeypatch.delenv(PASS_ENV_VAR, raising=False)
        monkeypatch.delenv(PASSFILE_ENV_VAR, raising=False)

        with raises(ArgumentError) as exc_info:
            validate_password(True)

        assert "environment variable" in str(exc_info.value)

    def test_raises_when_password_enabled_and_env_empty(self, monkeypatch) -> None:
        monkeypatch.setenv(PASS_ENV_VAR, "")
        monkeypatch.delenv(PASSFILE_ENV_VAR, raising=False)

        with raises(ArgumentError):
            validate_password(True)

    def test_passes_when_password_disabled_and_no_env_set(self, monkeypatch) -> None:
        monkeypatch.delenv(PASS_ENV_VAR, raising=False)
        monkeypatch.delenv(PASSFILE_ENV_VAR, raising=False)

        assert validate_password(False) is None

    def test_returns_none_when_password_disabled_even_if_env_set(self, monkeypatch) -> None:
        monkeypatch.setenv(PASS_ENV_VAR, "secret")

        assert validate_password(False) is None

    def test_returns_password_from_env(self, monkeypatch) -> None:
        monkeypatch.setenv(PASS_ENV_VAR, "secret")
        monkeypatch.delenv(PASSFILE_ENV_VAR, raising=False)

        assert validate_password(True) == "secret"

    def test_returns_password_from_passfile(self, monkeypatch, tmp_path: Path) -> None:
        passfile = (tmp_path / "passfile.txt")
        passfile.write_text("file secret")
        monkeypatch.setenv(PASSFILE_ENV_VAR, str(passfile))
        monkeypatch.delenv(PASS_ENV_VAR, raising=False)

        assert validate_password(True) == "file secret"

    def test_strips_newline_from_passfile(self, monkeypatch, tmp_path: Path) -> None:
        passfile = (tmp_path / "passfile.txt")
        passfile.write_text("file secret\n")
        monkeypatch.setenv(PASSFILE_ENV_VAR, str(passfile))
        monkeypatch.delenv(PASS_ENV_VAR, raising=False)

        assert validate_password(True) == "file secret"

    def test_raises_when_passfile_is_empty(self, monkeypatch, tmp_path: Path) -> None:
        passfile = (tmp_path / "passfile.txt")
        passfile.write_text("")
        monkeypatch.setenv(PASSFILE_ENV_VAR, str(passfile))
        monkeypatch.delenv(PASS_ENV_VAR, raising=False)

        with raises(ArgumentError) as exc_info:
            validate_password(True)

        assert "is empty" in str(exc_info.value)

    def test_raises_when_passfile_is_whitespace_only(self, monkeypatch, tmp_path: Path) -> None:
        passfile = (tmp_path / "passfile.txt")
        passfile.write_text("   \n\t\n")
        monkeypatch.setenv(PASSFILE_ENV_VAR, str(passfile))
        monkeypatch.delenv(PASS_ENV_VAR, raising=False)

        with raises(ArgumentError):
            validate_password(True)

    def test_env_takes_precedence_over_passfile(self, monkeypatch, tmp_path: Path) -> None:
        passfile = (tmp_path / "passfile.txt")
        passfile.write_text("file secret")
        monkeypatch.setenv(PASS_ENV_VAR, "secret")
        monkeypatch.setenv(PASSFILE_ENV_VAR, str(passfile))

        assert validate_password(True) == "secret"

    def test_raises_when_passfile_does_not_exist(self, monkeypatch) -> None:
        monkeypatch.setenv(PASSFILE_ENV_VAR, "/nonexistent/passfile.txt")
        monkeypatch.delenv(PASS_ENV_VAR, raising=False)

        with raises(FileNotFoundError):
            validate_password(True)


class TestModeArg:
    """ Tests for mode_arg function.
    """

    def test_raises_when_mode_incorrect (self) -> None:
        mode = "fandango"

        with raises(ArgumentTypeError) as exc_info:
            mode_arg(mode)

        assert "Mode must be" in str(exc_info.value)

    def test_allows_setting_backup (self) -> None:
        mode = 'b'
        result = mode_arg(mode)
        assert Mode.BACKUP == result

        mode = "backup"
        result = mode_arg(mode)
        assert Mode.BACKUP == result

    def test_allows_setting_restore (self) -> None:
        mode = 'r'
        result = mode_arg(mode)
        assert Mode.RESTORE == result

        mode = "restore"
        result = mode_arg(mode)
        assert Mode.RESTORE == result


class TestParseArgs:
    """ Tests for parse_args function.
    """

    def test_default_mode_backup (self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", origin, target]

            result = parse_args()

            assert result.mode is Mode.BACKUP
        finally:
            sys.argv = original_argv

    def test_allows_setting_mode_backup (self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", origin, target, 'b']
            result = parse_args()
            assert result.mode is Mode.BACKUP

            sys.argv = ["prog", origin, target, 'backup']
            result = parse_args()
            assert result.mode is Mode.BACKUP
        finally:
            sys.argv = original_argv

    def test_allows_setting_mode_restore (self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", origin, target, 'r']
            result = parse_args()
            assert result.mode is Mode.RESTORE

            sys.argv = ["prog", origin, target, 'restore']
            result = parse_args()
            assert result.mode is Mode.RESTORE
        finally:
            sys.argv = original_argv

    def test_wary_default_false(self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", origin, target]

            result = parse_args()

            assert result.wary is False
        finally:
            sys.argv = original_argv

    def test_timestamp_default_false(self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", origin, target]

            result = parse_args()

            assert result.timestamp is False
        finally:
            sys.argv = original_argv

    def test_log_default_false(self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", origin, target]

            result = parse_args()

            assert result.log is False
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

    def test_quiet_default_false(self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", origin, target]

            result = parse_args()

            assert result.quiet is False
        finally:
            sys.argv = original_argv

    def test_allows_setting_up_wary(self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", "-w", origin, target]

            result = parse_args()

            assert result.wary is True
        finally:
            sys.argv = original_argv

    def test_allows_setting_up_timestamp(self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", "-t", origin, target]

            result = parse_args()

            assert result.timestamp is True
        finally:
            sys.argv = original_argv

    def test_allows_setting_up_log(self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", "-l", origin, target]

            result = parse_args()

            assert result.log is True
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

    def test_allows_setting_up_quiet(self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", "-q", origin, target]

            result = parse_args()

            assert result.quiet is True
        finally:
            sys.argv = original_argv

    def test_allows_setting_log_file(self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", "-L", "logfile.txt", origin, target]

            result = parse_args()

            assert log_file is not None
            assert isinstance(result.log_file, Path)
        finally:
            sys.argv = original_argv

    def test_defines_origin_target_as_paths(self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", origin, target]

            result = parse_args()

            assert isinstance(result.origin, Path)
            assert isinstance(result.target, Path)
        finally:
            sys.argv = original_argv

    def test_setting_log_file_also_sets_log(self, tmp_path: Path) -> None:
        origin = str(tmp_path / "origin")
        target = str(tmp_path / "target")
        (tmp_path / "origin").mkdir()

        original_argv = sys.argv
        try:
            sys.argv = ["prog", "-L", "logfile.txt", origin, target]

            result = parse_args()

            assert result.log is True
        finally:
            sys.argv = original_argv
