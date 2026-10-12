# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

from pathlib import Path
from datetime import datetime, timezone

from wit_backup.log import (
    log_timestamp,
    TIMESTAMP_FILE,
)


class TestLogTimestamp:
    """ Tests for log_timestamp function.
    """

    def test_creates_logfile_if_not__exist(self, tmp_path: Path) -> None:
        log_timestamp(tmp_path, "START")

        assert (tmp_path / TIMESTAMP_FILE).exists()

    def test_appends_to_logfile_not_overwrite(self, tmp_path: Path) -> None:
        ts_file = (tmp_path / TIMESTAMP_FILE)
        ts_file.write_text("bang")

        log_timestamp(tmp_path, "START")

        assert "bang" in ts_file.read_text()

    def test_returns_current_datetime_UTC(self, tmp_path: Path) -> None:
        dt = log_timestamp(tmp_path, "START")

        now = datetime.now(timezone.utc)

        # direct comparison would fail if dt not in utc
        assert dt.replace(microsecond=0) == now.replace(microsecond=0)

    def test_includes_entry_and_date(self, tmp_path: Path) -> None:
        entry = "START"
        time = log_timestamp(tmp_path, entry)

        with open((tmp_path / TIMESTAMP_FILE), "r") as l:
            content = l.read()

            assert entry in content
            assert str(time.replace(microsecond=0)) in content