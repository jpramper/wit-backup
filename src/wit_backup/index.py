# Copyright Juan Pablo Ramirez 2026

import logging
from pathlib import Path
from hashlib import file_digest

INDEX_FILE = "_backup_index_"


def create_index(dir: Path) -> dict:
  """ Create an index file with a list of filenames and their hash.
  """
  logging.debug(f"----- creating index for {dir}")
  index = dict()

  for item in dir.iterdir():
    if item.is_file():
      with item.open("rb") as f:
        # for every file in dir, get the hash and add to index dictionary
        hash = file_digest(f, "md5")
        index[item.name] = hash.hexdigest()
        logging.debug(f"{item.name} {index[item.name]}")

  return index


def write_index(index: dict, dir: Path) -> bool:
  """ Write a file index dictionary to fs. overwrites if preexisting.
  """
  index_filename = Path(dir, INDEX_FILE)
  # if no files, write empty index to signal folder was checked
  if len(index) == 0:
    index_filename.touch()
    logging.debug(f"wrote EMPTY index for folder: {dir}")
    return True

  # write every dict item to new (overwrite) index file
  with open(index_filename, "w") as index_file:
    for key, val in index.items():
      index_file.write(f"{key}/{val}\n")

  logging.debug(f"wrote index for folder: {dir}")
  return True


def read_index(index_path: Path) -> dict:
  """ Read and load a file index to memory.

  Args:
    index_path: Path to index file. Must already include index file name.

  Returns:
    Empty index (dict) if no index file, populated otherwise. 
  """
  index = dict()
  if not index_path.exists() or index_path.name != INDEX_FILE:
    return index
  
  with open(index_path, "r") as i:
    for line in i:
      name, hash = line.split("/")
      index[name] = hash.rstrip("\n")
  
  logging.debug(f"reading index at {index_path}; {len(index)} items")
  return index


def indexes_mismatch(origin_index: dict, target_dir: Path) -> bool:
  """ Compare an origin file index with an unknown target dir. Returns true if mismatch.
  """
  # get what should be the target index file and check existence
  target_index_file = Path(target_dir, INDEX_FILE)
  if not target_index_file.exists():
    return True

  # if it exists, read it and compare with origin index
  target_index = read_index(target_index_file)
  if origin_index == target_index:
    return False

  # default to false; backup just in case
  return True
