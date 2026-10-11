# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

# Index file manipulation. Indexes are files created on every folder of the target with 
# filenames/hashes of files zipped in that folder.

import logging
from pathlib import Path
from hashlib import file_digest

# Filename for index files. Note if this changes, backups made before the change with a different
# filename will fail to find previous indexes and will re-backup everything.
INDEX_FILE = "_index_"


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


def write_index(index: dict, dir: Path) -> Path:
    """ 
    Write a file index dictionary to fs. overwrites if preexisting.
    Returns the Path to the index.
    """
    index_filename = Path(dir, INDEX_FILE)
    # if no files, write empty index to signal folder was checked
    if len(index) == 0:
        index_filename.touch()
        logging.debug(f"wrote EMPTY index for folder: {dir}")
        return index_filename

    # write every dict item to new (overwrite) index file
    with open(index_filename, "w") as index_file:
        for key, val in index.items():
            index_file.write(f"{key}/{val}\n")

    logging.debug(f"wrote index for folder: {dir}")
    return index_filename


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

    if not index_path.is_file():
        raise IsADirectoryError(f"{index_path} is not a file")

    try:
      with open(index_path, "r") as i:
          for line in i:
              if len(line.split("/")) == 2: # protection against empty lines
                  name, hash = line.split("/")
                  index[name] = hash.rstrip("\n")
    except Exception as e:
        logging.info(f"corrupted index at {index_path}")
        index = dict()
    
    logging.debug(f"read index at {index_path}; {len(index)} items")
    return index


def indexes_mismatch(origin_index: dict, target_dir: Path) -> bool:
    """ 
    Compare an origin file index with an index in an unknown target dir. 
    Returns true if mismatch.
    """
    # get what should be the target index file and check existence
    target_index_file = Path(target_dir, INDEX_FILE)
    if not target_index_file.exists():
        return True

    # if it exists, read it and compare with origin index
    target_index = read_index(target_index_file)
    if origin_index == target_index:
        return False

    # default to true; backup just in case
    return True
