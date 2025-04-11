import faiss
import numpy as np
from config import Config
import os
import pickle
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.index = None
        self.document_ids = []
        self.dimension = 768  # Updated to match the embedding size of `all-mpnet-base-v2`
        self.load_index()
        
    def load_index(self):
        if os.path.exists(Config.VECTOR_STORE_PATH):
            try:
                with open(Config.VECTOR_STORE_PATH, 'rb') as f:
                    data = pickle.load(f)
                    self.index = faiss.deserialize_index(data['index'])
                    self.document_ids = data['document_ids']
                    self.dimension = data['dimension']
                logger.info("Vector index loaded successfully")
            except Exception as e:
                logger.error(f"Error loading vector index: {str(e)}")
                self._create_new_index()
        else:
            self._create_new_index()
            
    def _create_new_index(self):
        self.index = faiss.IndexFlatL2(self.dimension)
        self.document_ids = []
        logger.info("Created new vector index")
        
    def save_index(self):
        try:
            data = {
                'index': faiss.serialize_index(self.index),
                'document_ids': self.document_ids,
                'dimension': self.dimension
            }
            with open(Config.VECTOR_STORE_PATH, 'wb') as f:
                pickle.dump(data, f)
            logger.info("Vector index saved successfully")
        except Exception as e:
            logger.error(f"Error saving vector index: {str(e)}")
            raise
            
    def add_document(self, embedding, document_id):
        try:
            if not isinstance(embedding, list):
                raise ValueError("Embedding must be a list")
                
            embedding_array = np.array([embedding], dtype='float32')
            
            # Handle dimension mismatch
            if embedding_array.shape[1] != self.dimension:
                raise ValueError(f"Embedding dimension mismatch. Expected {self.dimension}, got {embedding_array.shape[1]}")
                
            self.index.add(embedding_array)
            self.document_ids.append(document_id)
            self.save_index()
            logger.info(f"Document added to vector store: {document_id}")
        except Exception as e:
            logger.error(f"Error adding document to vector store: {str(e)}")
            raise
            
    def search(self, query_embedding, k=5):
        try:
            if not isinstance(query_embedding, list):
                raise ValueError("Query embedding must be a list")
                
            query_array = np.array([query_embedding], dtype='float32')
            
            # Handle dimension mismatch
            if query_array.shape[1] != self.dimension:
                raise ValueError(f"Query dimension mismatch. Expected {self.dimension}, got {query_array.shape[1]}")
                
            distances, indices = self.index.search(query_array, k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx >= 0 and idx < len(self.document_ids):
                    results.append({
                        'document_id': self.document_ids[idx],
                        'distance': float(distances[0][i])
                    })
                    
            return results
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            raise
