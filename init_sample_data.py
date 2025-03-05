#!/usr/bin/env python3
"""
Initialize the database with sample data.
This script is run when INIT_DB is set to true.
"""

import os
import sys
import time
from utils.db import init_db, add_custom_gpu, add_custom_llm_model, SessionLocal, GPUModel, LLMModel

def main():
    print("Initializing database...")
    
    # Initialize database schema
    init_db()
    
    # Create a database session
    db = SessionLocal()
    if db is None:
        print("Error: Could not connect to database.")
        sys.exit(1)
    
    try:
        # Add sample GPU models if they don't exist
        default_gpus = [
            "RTX 4090", 
            "RTX 4080S", 
            "ADA 6000", 
            "RTX 3090", 
            "A100", 
            "H100"
        ]
        
        for gpu_name in default_gpus:
            # Check if GPU already exists
            existing = db.query(GPUModel).filter(GPUModel.name == gpu_name).first()
            if not existing:
                # Use the add_custom_gpu function to add the GPU
                add_custom_gpu(gpu_name)
                print(f"Added GPU: {gpu_name}")
        
        # Add sample LLM models if they don't exist
        default_models = [
            "llama3-latest", 
            "llama3-8b-instruct", 
            "llama2-7b-chat", 
            "llama3-70b", 
            "mistral-7b", 
            "claude-3-opus"
        ]
        
        for model_name in default_models:
            # Check if model already exists
            existing = db.query(LLMModel).filter(LLMModel.name == model_name).first()
            if not existing:
                # Use the add_custom_llm_model function to add the model
                add_custom_llm_model(model_name)
                print(f"Added LLM model: {model_name}")
        
        print("Database initialization complete!")
    
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    main() 