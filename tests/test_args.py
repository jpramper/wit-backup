# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

from pathlib import Path

from wit_backup.args import (
  origin_path
)


class TestOriginPath: 
  """Tests for origin_path function.
  """

  def test_fails_when_origin_not_exists(self) -> None:
    pass


class TestTargetPath:
  """Tests for target_path function.
  """

  def test_fails_when_target_exists_as_file(self) -> None:
    pass


class TestParseArgs:
  """Tests for parse_args function.
  """

  def test_verbose_default_false(self) -> None:
    pass
