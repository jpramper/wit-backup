# wit-backup

Backup program for Wit (personal file server)

Backup is done on a per-folder basis: Files in every folder in the origin will be zipped into a single zip file into the respective folder in the destination, and an index file with files/hashes included in the zip will be created. 

Restoration will restore the folder structure as it was backed up onto the specified target.

```
origin
  ├── subfolder
  │     ├── file_A.smpl
  │     └── file_B.smpl
  └── file_C.smpl
```

```
target
  ├── subfolder
  │     ├── _backup_.zip
  │     └── _index_
  ├── _backup_.zip
  └── _index_
```

Further backups will first check the index in each folder for discrepancies, and only refresh the backup zip (and index) if differences are found.

As steps:
1) Mirrors the folder structure of the origin into the target. 
2) Compares files in every origin folder with files recorded in an index file in every folder of the target.
3) If changes detected or no index is found, creates an updated index and zips files in current origin folder to the matching target folder.

This program can recursively remove directories: SHOULD NOT BE RUN AS ROOT. Run backups with least privilege necessary.

## Installation

Requires python 3.12+

Install a built wheel with 
```
pip install <wit_wheel>.whl
```

## Running

Run with 
```
wit-backup [opts] <origin> <destination> [<mode>]
```
- opts: 
  - `-w` prevent backup if origin is empty. prevent restore if target is not empty.
       (important if origin's drive fails, to not delete the backup on next backup run)
  - `-t` append UTC timestamps of operation start/complete at a log file in target root (\<target\>/wb-timestamps.log)
  - `-l` write events into (\<target\>/wb-runtime.log) or if set, wherever `-L` specifies
  - `-L` specify a logfile to write events to. activates `-l` as well if set
  - `-p` lock/unlock zip files with a password, taken from the `WIT_BACKUP_PASS` environment variable, or from the file pointed to by `WIT_BACKUP_PASSFILE`. `WIT_BACKUP_PASS` takes precedence.
  - `-d` delete destination folder before backup/restore (careful!)
  - `-v` added verbosity (debug messages added)
  - `-q` reduced verbosity (only errors print)
- \<origin\> Path to folder to backup or restore from.
- \<destination\> Path to destination folder. May not exist and will be created.
- \<mode\> defaults to backup
  - `b` create a backup (default)
  - `r` restore a backup

## Local Development Environment Setup
Setup a python virtual environment on project root:
```
python -m venv .venv
source .venv/bin/activate
```
Then install the project in editable mode (this includes dev dependencies):
```
pip install -e ".[dev]"
```
You can then run the project with
```
wit-backup [opts] <origin> <target>
```

Exit venv with "deactivate".

Or without a venv you'll be able to run the project directly with
```
python -m wit_backup.main [opts] <origin> <target>
```

## Unit Tests

After setting up the dev env above, just run
```
pytest
```

## Scans & Linting

Currently using ruff for linting and bandit for SAST:
```
ruff check
bandit -r src/
```

## Local Build

Setuptools is used to package the wheel:
```
python -m build --wheel
```
Note you'll need the venv active.