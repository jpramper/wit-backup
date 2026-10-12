# wit-backup

Backup program for Wit (personal file server)

Backup is done on a per-folder basis: Files in every folder in the origin will be zipped into a single zip file into the respective folder in the destination, and an index file with files/hashes included in the zip will be created. 


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

## Running

Run with 
```
wit-backup [opts] <origin> <destination>
```
- opts: 
  - ```-w``` prevent backup if origin is empty 
       (important if origin's drive fails, to not delete the backup on next run)
  - ```-t``` append UTC timestamps of start/complete at a log file in target root (\<target\>/wb-timestamps.log)
  - ```-r``` restore a backup instead of creating a new backup
  - ```-d``` delete destination folder before backup (careful!)
  - ```-v``` added verbosity (debug messages added)
  - ```-q``` reduced verbosity (only errors print)
- \<origin\> Path to folder to backup or restore from.
- \<destination\> Path to destination folder. May not exist and will be created.

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
pytest --cov-report=term-missing
```

## Local Build

Setuptools is used to package the wheel:
```
python -m build --wheel
```
Note you'll need the venv active.