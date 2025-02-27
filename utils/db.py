import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from the Benchmarks directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get database credentials
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_NAME = os.getenv('POSTGRES_DB')

# Create database URL
POSTGRES_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine
engine = create_engine(POSTGRES_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

class ChatAudit(Base):
    __tablename__ = "chat_audits"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, index=True)
    gpu_name = Column(String, index=True)
    user_message = Column(Text)
    assistant_message = Column(Text)
    is_good_response = Column(Boolean)
    feedback = Column(Text, nullable=True)
    cpu_usage = Column(Float)
    gpu_usage = Column(Float)
    ram_usage = Column(Float)
    vram_usage = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 