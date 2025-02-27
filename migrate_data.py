#!/usr/bin/env python3
"""
Script to migrate existing benchmark data to the new directory structure.
"""

import os
import shutil
from pathlib import Path

# Define source and destination directories
SOURCE_DIRS = ['RTX4090', 'RTX4080S', 'ADA6000', 'ADA6000-Latest']
DEST_DIR = 'data'

def migrate_data():
    """Migrate data from old structure to new structure."""
    print("Starting data migration...")
    
    # Get the current directory (should be Benchmarks)
    current_dir = Path(os.getcwd())
    if current_dir.name != 'Benchmarks':
        # If not in Benchmarks directory, check if Benchmarks is a subdirectory
        if (current_dir / 'Benchmarks').exists():
            os.chdir('Benchmarks')
            print("Changed directory to Benchmarks")
        else:
            print("Warning: Not in Benchmarks directory. Please run this script from the Benchmarks directory.")
    
    # Create destination directory if it doesn't exist
    os.makedirs(DEST_DIR, exist_ok=True)
    
    # Migrate each source directory
    for source_dir in SOURCE_DIRS:
        source_path = Path(source_dir)
        dest_path = Path(DEST_DIR) / source_dir
        
        # Skip if source directory doesn't exist
        if not source_path.exists():
            print(f"Source directory {source_path} does not exist. Skipping.")
            continue
        
        # Create destination directory
        os.makedirs(dest_path, exist_ok=True)
        
        # Copy all files from source to destination
        for file_path in source_path.glob('*'):
            if file_path.is_file():
                dest_file = dest_path / file_path.name
                print(f"Copying {file_path} to {dest_file}")
                shutil.copy2(file_path, dest_file)
            elif file_path.is_dir():
                dest_subdir = dest_path / file_path.name
                print(f"Copying directory {file_path} to {dest_subdir}")
                shutil.copytree(file_path, dest_subdir, dirs_exist_ok=True)
    
    print("Data migration complete!")

if __name__ == "__main__":
    migrate_data() 