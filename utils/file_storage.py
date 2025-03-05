"""
File storage utility module that can use either S3 or local storage.
This provides a unified interface for reading and writing files regardless of storage backend.
"""

import os
import logging
from pathlib import Path
import pandas as pd
from io import BytesIO, StringIO
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Check if S3 should be used
USE_S3_STORAGE = os.getenv('USE_S3_STORAGE', 'true').lower() == 'true'

# Import S3 utilities if needed
if USE_S3_STORAGE:
    try:
        from .s3 import (
            is_s3_available, 
            upload_file_to_s3, 
            upload_string_to_s3, 
            download_file_from_s3, 
            list_files_in_s3, 
            read_csv_from_s3, 
            file_exists_in_s3
        )
        # Check if S3 is available
        S3_AVAILABLE = is_s3_available()
        if not S3_AVAILABLE:
            logger.warning("S3 storage is enabled but not available. Using local storage instead.")
    except ImportError:
        logger.warning("S3 utilities could not be imported. Using local storage instead.")
        S3_AVAILABLE = False
else:
    S3_AVAILABLE = False

# Define data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")

# Ensure directories exist
for directory in [DATA_DIR, LOGS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def is_using_s3():
    """Check if S3 storage is being used."""
    return USE_S3_STORAGE and S3_AVAILABLE

def read_file(file_path):
    """Read a file from either S3 or local storage.
    
    Args:
        file_path (str): Path to the file. Can be a local path or an S3 key.
        
    Returns:
        str or None: File content as string if successful, None otherwise
    """
    # Check if this is an S3 path
    if file_path.startswith("s3://") and is_using_s3():
        s3_key = file_path.replace("s3://", "")
        return download_file_from_s3(s3_key)
    
    # Check if this is a direct S3 key
    if is_using_s3() and not os.path.exists(file_path) and not file_path.startswith("/"):
        # Try to download from S3 first
        content = download_file_from_s3(file_path)
        if content is not None:
            return content
    
    # Fall back to local file
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"File not found: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return None

def write_file(content, file_path, upload_to_s3=True, s3_key=None):
    """Write content to a file in either S3 or local storage.
    
    Args:
        content (str): Content to write
        file_path (str): Path to the local file
        upload_to_s3 (bool): Whether to upload to S3 if available
        s3_key (str, optional): Custom S3 key/path to use. If None, file_path will be used.
        
    Returns:
        str or None: Path to the file if successful, None otherwise
    """
    # Always write to local file first
    try:
        # Ensure directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        # Upload to S3 if available
        if upload_to_s3 and is_using_s3():
            # Use custom S3 key if provided, otherwise use file_path
            if s3_key is None:
                s3_key = file_path
                if s3_key.startswith("./"):
                    s3_key = s3_key[2:]
            
            upload_success = upload_string_to_s3(content, s3_key)
            if upload_success:
                return f"s3://{s3_key}"
        
        return file_path
    except Exception as e:
        logger.error(f"Error writing file {file_path}: {str(e)}")
        return None

def read_csv(file_path):
    """Read a CSV file from either S3 or local storage.
    
    Args:
        file_path (str): Path to the file. Can be a local path or an S3 key.
        
    Returns:
        DataFrame or None: Pandas DataFrame if successful, None otherwise
    """
    # Check if this is an S3 path
    if file_path.startswith("s3://") and is_using_s3():
        s3_key = file_path.replace("s3://", "")
        return read_csv_from_s3(s3_key)
    
    # Check if this is a direct S3 key
    if is_using_s3() and not os.path.exists(file_path) and not file_path.startswith("/"):
        # Try to read from S3 first
        df = read_csv_from_s3(file_path)
        if df is not None:
            return df
    
    # Fall back to local file
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        logger.warning(f"CSV file not found: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error reading CSV file {file_path}: {str(e)}")
        return None

def list_files(directory=None, prefix=None):
    """List files in either S3 or local storage.
    
    Args:
        directory (str, optional): Local directory to list files from
        prefix (str, optional): S3 prefix to list files from
        
    Returns:
        list: List of file paths
    """
    files = []
    
    # List files from S3 if available
    if is_using_s3() and prefix is not None:
        s3_files = list_files_in_s3(prefix)
        files.extend([f"s3://{f}" for f in s3_files])
    
    # List files from local directory
    if directory is not None and os.path.exists(directory):
        local_files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        files.extend(local_files)
    
    return files

def file_exists(file_path):
    """Check if a file exists in either S3 or local storage.
    
    Args:
        file_path (str): Path to the file. Can be a local path or an S3 key.
        
    Returns:
        bool: True if file exists, False otherwise
    """
    # Check if this is an S3 path
    if file_path.startswith("s3://") and is_using_s3():
        s3_key = file_path.replace("s3://", "")
        return file_exists_in_s3(s3_key)
    
    # Check if this is a direct S3 key
    if is_using_s3() and not os.path.exists(file_path) and not file_path.startswith("/"):
        # Try to check in S3 first
        if file_exists_in_s3(file_path):
            return True
    
    # Fall back to local file
    return os.path.exists(file_path)

def get_file_path(base_path, filename, check_s3=True):
    """Get the appropriate file path, checking S3 first if enabled.
    
    Args:
        base_path (str): Base path or directory
        filename (str): Filename to append to base path
        check_s3 (bool): Whether to check S3 first
        
    Returns:
        str: Full path to the file (local or S3)
    """
    if check_s3 and is_using_s3():
        # Check if file exists in S3
        s3_key = os.path.join(base_path, filename).replace("\\", "/")
        if file_exists_in_s3(s3_key):
            return f"s3://{s3_key}"
    
    # Fall back to local path
    return os.path.join(base_path, filename) 