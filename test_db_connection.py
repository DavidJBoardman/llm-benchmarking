import os
import time
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get database credentials
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB')

# Create database URL
POSTGRES_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"Attempting to connect to database at: {DB_HOST}:{DB_PORT}")
print(f"Database name: {DB_NAME}")
print(f"Database user: {DB_USER}")

# Try to connect with retry logic
max_retries = 5
retry_interval = 5
retries = 0

while retries < max_retries:
    try:
        print(f"Connection attempt {retries + 1}...")
        engine = create_engine(POSTGRES_URI)
        
        # Test connection by executing a simple query
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Database connection successful!")
            print("Query result:", result.fetchone())
            
            # Get database version
            version = conn.execute(text("SELECT version()"))
            print("Database version:", version.fetchone()[0])
            
            # List tables
            tables = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
            print("Tables in database:")
            for table in tables:
                print(f"  - {table[0]}")
                
        break
    except Exception as e:
        retries += 1
        print(f"Connection failed: {str(e)}")
        if retries >= max_retries:
            print(f"Failed to connect after {max_retries} attempts.")
            break
        print(f"Retrying in {retry_interval} seconds...")
        time.sleep(retry_interval) 