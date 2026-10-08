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


class TestWriteIndex:
  """Tests for write_index function.
  """

  def test_writes_empty_file_when_index_empty(self) -> None:
    pass


class TestReadIndex:
  """Tests for read_index function.
  """

  def returns_empty_index_when_target_not_exists(self) -> None:
    pass


class TestIndexesMismatch:
  """Tests for indexes_mismatch function.
  """

  def true_when_target_not_exists(self) -> None:
    pass
