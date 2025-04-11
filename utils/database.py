from pymongo import MongoClient
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoDB:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.MONGO_DB_NAME]
        self.documents = self.db.documents
        
    def insert_document(self, document_data):
        try:
            result = self.documents.insert_one(document_data)
            logger.info(f"Document inserted with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting document: {str(e)}")
            raise

            
    def get_document(self, document_id):
        try:
            document = self.documents.find_one({"_id": document_id})
            if document:
                document['_id'] = str(document['_id'])
            return document
        except Exception as e:
            logger.error("Error fetching document", error=str(e))
            raise
            
    def get_all_documents(self):
        try:
            documents = list(self.documents.find({}))
            for doc in documents:
                doc['_id'] = str(doc['_id'])
            return documents
        except Exception as e:
            logger.error("Error fetching all documents", error=str(e))
            raise