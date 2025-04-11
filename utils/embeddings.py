# from sentence_transformers import SentenceTransformer
# from config import Config
# import numpy as np
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class EmbeddingGenerator:
#     _instance = None
    
#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super(EmbeddingGenerator, cls).__new__(cls)
#             cls._instance.model = SentenceTransformer(Config.EMBEDDING_MODEL)
#         return cls._instance
    
#     def generate_embedding(self, text):
#         try:
#             if not text or not isinstance(text, str):
#                 raise ValueError("Text must be a non-empty string")
                
#             embedding = self.model.encode(text)
#             return embedding.tolist()  # Ensure it's a list for DB compatibility
#         except Exception as e:
#             logger.error(f"Error generating embedding: {str(e)}")
#             raise
from sentence_transformers import SentenceTransformer
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingGenerator, cls).__new__(cls)
            cls._instance.model = SentenceTransformer(Config.EMBEDDING_MODEL)
        return cls._instance
    
    def generate_embedding(self, text):
        try:
            if not text or not isinstance(text, str):
                raise ValueError("Text must be a non-empty string")
                
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
