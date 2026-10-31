# Changelog

Changes to wit-backup are logged here.


## [Unreleased]

### Added
- `-p` option to provide a password to use to lock/unlock backup zipfiles during a backup or a restore.


## [1.2.1] - 2026-10-26

### Fixed
- Modified backup script so that an unexpected interrupt (eg unexpected shutdown)
does not leave an incomplete zip marked as completed. Next run will re-attempt it.


## [1.2.0] - 2026-10-21

Added backup restoration functionality.

### Removed
- `-r` restore option flag

### Added
- \<mode\> optional argument, defaults to backup and controls program mode.
- Backup restoration functionality.


## [1.1.0] - 2026-10-14

Added logging and quality-of-life options.

### Added 
- `--wary` option to avoid destructive backups when origin is lost
- `--timestamp` option to log start and complete time on -target-/wb-timestamps.log
- `--log` option to log messages on -target-/wb-runtime.log by default, 
          or wherever `--logfile` specifies
- `--log-file` option to specify a logfile to write logging messages to. 
               automatically activates `--log` as well if set
- `--quiet` option to reduce verbosity to error-only messages


## [1.0.0] - 2026-10-09

Initial release. Complete base backup functionality.

### Added
- Complete project structure
- Base backup functionality
- `--delete` functionality to clear target contents
- `--verbose` functionality to increase verbosity and log debug info
- Complete unit test suite for development
