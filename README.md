# wit-backup

Backup program for Wit (personal file server)

This program can recursively remove directories: 
- SHOULD NOT BE RUN AS ROOT.

## Local Development Environment Setup
Setup a python virtual environment on project root:
```
python3 -m venv .venv
source .venv/bin/activate
```
Then install the project in editable mode:
```
pip install -e .
```
You'll be able to edit the source and run the project with
```
python -m wit_backup.main [opts] <origin> <target>
```

Exit venv with "deactivate".

## Running Locally

Run with 
```
wit-backup [opts] origin destination
```
- opts: 
  - -v for verbosity
  - -d to delete destination folder before backup (careful!)
- origin: Path to folder to backup.
- destination: Path to destination folder. May not exist and will be created.

## Logic

Backup is done on a per-folder basis: Files in every folder in the origin will be zipped into a single zip file into the respective folder in the destination, and an index file with files/hashes included in the zip will be created. 

Further backups will first check the index in each folder for discrepancies, and only refresh the backup zip (and index) if differences are found.

As steps:
1) Mirrors the folder structure of the origin into the target. 
2) Compares files in every origin folder with files recorded in an index file in every folder of the target.
3) If changes detected or no index, creates an updated index and zips files in current origin folder to matching target folder.