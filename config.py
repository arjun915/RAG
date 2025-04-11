# config.py

import os
from pathlib import Path
from dotenv import load_dotenv  # Add this line
load_dotenv()
class Config:
    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI", "your_mongodb_atlas_connection_string")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "rag_faq")
    
    # Embedding Model Configuration

    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2")
    # EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Change this to your embedding model
    LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"  
    TOGETHER_AI_API_KEY =  os.environ["TOGETHER_AI_API_KEY"]
    
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "faiss_index")