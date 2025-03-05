#!/usr/bin/env python3
"""
Initialize the database with sample data for testing.
This script will create sample GPU and LLM models in the database.
"""

import os
import sys
from utils.db import SessionLocal, GPUModel, LLMModel, init_db

def init_sample_data():
    """Initialize the database with sample data."""
    print("Initializing database with sample data...")
    
    # Initialize database schema
    init_db()
    
    # Create a database session
    db = SessionLocal()
    if db is None:
        print("Error: Could not connect to database.")
        sys.exit(1)
    
    try:
        # Add sample GPU models
        default_gpus = [
            {"name": "RTX 4090", "is_custom": False},
            {"name": "RTX 4080S", "is_custom": False},
            {"name": "ADA 6000", "is_custom": False},
            {"name": "RTX 3090", "is_custom": True},
            {"name": "A100", "is_custom": True},
            {"name": "H100", "is_custom": True}
        ]
        
        for gpu_data in default_gpus:
            # Check if GPU already exists
            existing = db.query(GPUModel).filter(GPUModel.name == gpu_data["name"]).first()
            if not existing:
                gpu = GPUModel(**gpu_data)
                db.add(gpu)
                print(f"Added GPU: {gpu_data['name']}")
        
        # Add sample LLM models
        default_models = [
            {"name": "llama3-latest", "is_custom": False},
            {"name": "llama3-8b-instruct", "is_custom": False},
            {"name": "llama2-7b-chat", "is_custom": False},
            {"name": "llama3-70b", "is_custom": True},
            {"name": "mistral-7b", "is_custom": True},
            {"name": "claude-3-opus", "is_custom": True}
        ]
        
        for model_data in default_models:
            # Check if model already exists
            existing = db.query(LLMModel).filter(LLMModel.name == model_data["name"]).first()
            if not existing:
                model = LLMModel(**model_data)
                db.add(model)
                print(f"Added LLM model: {model_data['name']}")
        
        # Commit changes
        db.commit()
        print("Sample data initialization complete.")
    
    except Exception as e:
        print(f"Error initializing sample data: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_sample_data() 