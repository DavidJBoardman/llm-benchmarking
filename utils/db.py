import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import time

# Load environment variables from the Benchmarks directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get database credentials
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')  # Default to localhost if not specified
DB_PORT = os.getenv('POSTGRES_PORT', '5432')  # Default to 5432 if not specified
DB_NAME = os.getenv('POSTGRES_DB')

# Create database URL
POSTGRES_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Function to create engine with retry logic
def create_db_engine(uri, max_retries=5, retry_interval=5):
    """Create a database engine with retry logic for better reliability."""
    retries = 0
    while retries < max_retries:
        try:
            engine = create_engine(uri)
            # Test connection
            with engine.connect() as conn:
                print("Database connection successful.")
            return engine
        except Exception as e:
            retries += 1
            if retries >= max_retries:
                raise Exception(f"Failed to connect to database after {max_retries} attempts: {str(e)}")
            print(f"Database connection attempt {retries} failed. Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)

# Create engine with retry logic
try:
    engine = create_db_engine(POSTGRES_URI)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"Warning: Database connection failed: {str(e)}")
    print("Application will continue but database features will be disabled.")
    engine = None
    SessionLocal = None

# Create declarative base
Base = declarative_base()

class GPUModel(Base):
    """Table to store available GPU models"""
    __tablename__ = "gpu_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    is_custom = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class LLMModel(Base):
    """Table to store available LLM models"""
    __tablename__ = "llm_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    is_custom = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

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
    """Initialize the database schema."""
    if engine is not None:
        try:
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully.")
            
            # Initialize default GPU and LLM models if tables are empty
            db = SessionLocal()
            
            # Add default GPUs if none exist
            if db.query(GPUModel).count() == 0:
                default_gpus = ["RTX 4090", "RTX 4080S", "ADA 6000"]
                for gpu in default_gpus:
                    db.add(GPUModel(name=gpu, is_custom=False))
            
            # Add default LLM models if none exist
            if db.query(LLMModel).count() == 0:
                default_models = ["llama3-latest", "llama3-8b-instruct", "llama2-7b-chat"]
                for model in default_models:
                    db.add(LLMModel(name=model, is_custom=False))
            
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"Error creating database tables: {str(e)}")

def get_db():
    """Get a database session with error handling."""
    if SessionLocal is None:
        print("Database connection is not available.")
        return None
        
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_all_gpus():
    """Get all GPU models from the database."""
    if SessionLocal is None:
        return []
    
    try:
        db = SessionLocal()
        gpus = db.query(GPUModel).order_by(GPUModel.name).all()
        db.close()
        return gpus
    except Exception as e:
        print(f"Error fetching GPUs: {str(e)}")
        return []

def get_all_llm_models():
    """Get all LLM models from the database."""
    if SessionLocal is None:
        return []
    
    try:
        db = SessionLocal()
        models = db.query(LLMModel).order_by(LLMModel.name).all()
        db.close()
        return models
    except Exception as e:
        print(f"Error fetching LLM models: {str(e)}")
        return []

def add_custom_gpu(name):
    """Add a custom GPU model to the database."""
    if SessionLocal is None:
        return None
    
    try:
        db = SessionLocal()
        # Check if GPU already exists
        existing = db.query(GPUModel).filter(GPUModel.name == name).first()
        if existing:
            db.close()
            return existing
        
        # Add new GPU
        new_gpu = GPUModel(name=name, is_custom=True)
        db.add(new_gpu)
        db.commit()
        db.refresh(new_gpu)
        db.close()
        return new_gpu
    except Exception as e:
        print(f"Error adding custom GPU: {str(e)}")
        return None

def add_custom_llm_model(name):
    """Add a custom LLM model to the database."""
    if engine is None:
        return None
    
    try:
        db = SessionLocal()
        # Check if model already exists
        existing_model = db.query(LLMModel).filter(LLMModel.name == name).first()
        if existing_model:
            db.close()
            return existing_model
        
        # Create new model
        new_model = LLMModel(
            name=name,
            is_custom=True
        )
        db.add(new_model)
        db.commit()
        db.refresh(new_model)
        db.close()
        return new_model
    except Exception as e:
        print(f"Error adding custom LLM model: {str(e)}")
        return None

def delete_audit(audit_id):
    """Delete a chat audit by ID.
    
    Args:
        audit_id (int): The ID of the audit to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    if engine is None:
        return False
    
    try:
        db = SessionLocal()
        audit = db.query(ChatAudit).filter(ChatAudit.id == audit_id).first()
        if not audit:
            db.close()
            return False
        
        db.delete(audit)
        db.commit()
        db.close()
        return True
    except Exception as e:
        print(f"Error deleting audit: {str(e)}")
        return False

def update_audit(audit_id, **kwargs):
    """Update a chat audit by ID.
    
    Args:
        audit_id (int): The ID of the audit to update
        **kwargs: Fields to update (user_message, assistant_message, is_good_response, feedback)
        
    Returns:
        ChatAudit: The updated audit object if successful, None otherwise
    """
    if engine is None:
        return None
    
    try:
        db = SessionLocal()
        audit = db.query(ChatAudit).filter(ChatAudit.id == audit_id).first()
        if not audit:
            db.close()
            return None
        
        # Update fields
        allowed_fields = ['user_message', 'assistant_message', 'is_good_response', 'feedback']
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(audit, field, value)
        
        db.commit()
        db.refresh(audit)
        db.close()
        return audit
    except Exception as e:
        print(f"Error updating audit: {str(e)}")
        return None 