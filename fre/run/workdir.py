# ---------------- set up working directory structure
# Need to import variables: workDir, tmpOutputDir
from pathlib import Path
import os
import shutil
import sys

workDir = Path("/path/to/directory")

if workDir.is_dir():   #checks for existence and if path is directory
  if os.access(workDir, os.R_OK | os.W_OK):  #checks read and write permissions
    for item in work_dir.iterdir():
      #remove everything except temporary directory
      if item == tmp_output_dir: 
        continue
      try:
        # Delete all files, folders, and links
        if item.is_file() or item.is_symlink():
            item.unlink()  # Deletes individual files or symlinks
        elif item.is_dir():
            shutil.rmtree(item)  # Recursively deletes directories (rm -rf)
            
    except Exception as e:
        # Incase of a weird glitch, error instead of crash
        print(f"Skipped {item} due to error: {e}")
