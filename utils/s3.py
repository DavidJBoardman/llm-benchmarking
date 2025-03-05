import os
import boto3
import logging
from botocore.exceptions import ClientError
from io import BytesIO, StringIO
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get AWS credentials from environment variables
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'eu-west-2')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

# Initialize S3 client
try:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    logger.info("S3 client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing S3 client: {str(e)}")
    s3_client = None

def is_s3_available():
    """Check if S3 is available and properly configured."""
    if not S3_BUCKET_NAME or not s3_client:
        return False
    
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        return True
    except ClientError as e:
        logger.error(f"Error accessing S3 bucket: {str(e)}")
        return False

def upload_file_to_s3(local_file_path, s3_key):
    """Upload a file to S3 bucket.
    
    Args:
        local_file_path (str): Path to the local file
        s3_key (str): S3 object key (path in the bucket)
        
    Returns:
        bool: True if upload was successful, False otherwise
    """
    if not is_s3_available():
        logger.warning("S3 is not available. File will not be uploaded.")
        return False
    
    try:
        s3_client.upload_file(local_file_path, S3_BUCKET_NAME, s3_key)
        logger.info(f"Successfully uploaded {local_file_path} to s3://{S3_BUCKET_NAME}/{s3_key}")
        return True
    except ClientError as e:
        logger.error(f"Error uploading file to S3: {str(e)}")
        return False

def upload_string_to_s3(content, s3_key):
    """Upload a string content to S3 bucket.
    
    Args:
        content (str): String content to upload
        s3_key (str): S3 object key (path in the bucket)
        
    Returns:
        bool: True if upload was successful, False otherwise
    """
    if not is_s3_available():
        logger.warning("S3 is not available. Content will not be uploaded.")
        return False
    
    try:
        s3_client.put_object(Body=content, Bucket=S3_BUCKET_NAME, Key=s3_key)
        logger.info(f"Successfully uploaded content to s3://{S3_BUCKET_NAME}/{s3_key}")
        return True
    except ClientError as e:
        logger.error(f"Error uploading content to S3: {str(e)}")
        return False

def download_file_from_s3(s3_key, local_file_path=None):
    """Download a file from S3 bucket.
    
    Args:
        s3_key (str): S3 object key (path in the bucket)
        local_file_path (str, optional): Path to save the file locally
        
    Returns:
        str or None: File content as string if successful, None otherwise
    """
    if not is_s3_available():
        logger.warning("S3 is not available. File will not be downloaded.")
        return None
    
    try:
        if local_file_path:
            s3_client.download_file(S3_BUCKET_NAME, s3_key, local_file_path)
            logger.info(f"Successfully downloaded s3://{S3_BUCKET_NAME}/{s3_key} to {local_file_path}")
            return True
        else:
            response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
            content = response['Body'].read().decode('utf-8')
            logger.info(f"Successfully downloaded content from s3://{S3_BUCKET_NAME}/{s3_key}")
            return content
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            logger.warning(f"File not found in S3: s3://{S3_BUCKET_NAME}/{s3_key}")
        else:
            logger.error(f"Error downloading file from S3: {str(e)}")
        return None

def list_files_in_s3(prefix=''):
    """List files in S3 bucket with the given prefix.
    
    Args:
        prefix (str): Prefix to filter objects
        
    Returns:
        list: List of object keys
    """
    if not is_s3_available():
        logger.warning("S3 is not available. Cannot list files.")
        return []
    
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=prefix)
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]
        return []
    except ClientError as e:
        logger.error(f"Error listing files in S3: {str(e)}")
        return []

def read_csv_from_s3(s3_key):
    """Read a CSV file from S3 and return a pandas DataFrame.
    
    Args:
        s3_key (str): S3 object key (path in the bucket)
        
    Returns:
        DataFrame or None: Pandas DataFrame if successful, None otherwise
    """
    if not is_s3_available():
        logger.warning("S3 is not available. CSV will not be read.")
        return None
    
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        content = response['Body'].read()
        df = pd.read_csv(BytesIO(content))
        logger.info(f"Successfully read CSV from s3://{S3_BUCKET_NAME}/{s3_key}")
        return df
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            logger.warning(f"CSV file not found in S3: s3://{S3_BUCKET_NAME}/{s3_key}")
        else:
            logger.error(f"Error reading CSV from S3: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error parsing CSV from S3: {str(e)}")
        return None

def file_exists_in_s3(s3_key):
    """Check if a file exists in S3 bucket.
    
    Args:
        s3_key (str): S3 object key (path in the bucket)
        
    Returns:
        bool: True if file exists, False otherwise
    """
    if not is_s3_available():
        logger.warning("S3 is not available. Cannot check if file exists.")
        return False
    
    try:
        s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        logger.error(f"Error checking if file exists in S3: {str(e)}")
        return False 