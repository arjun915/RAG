from flask import Flask, request, jsonify,render_template
from flask_cors import CORS
from utils.database import MongoDB
from utils.embeddings import EmbeddingGenerator
from utils.vector_store import VectorStore
from utils.llm import LocalLLMService
from config import Config
# import structlog
import logging
import os
from functools import wraps
from bson import ObjectId  # Add at top of file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# structlog.configure(
#     processors=[
#         structlog.stdlib.filter_by_level,
#         structlog.stdlib.add_logger_name,
#         structlog.stdlib.add_log_level,
#         structlog.stdlib.PositionalArgumentsFormatter(),
#         structlog.processors.TimeStamper(fmt="iso"),
#         structlog.processors.JSONRenderer()
#     ],
#     context_class=dict,
#     logger_factory=structlog.stdlib.LoggerFactory(),
#     wrapper_class=structlog.stdlib.BoundLogger,
#     cache_logger_on_first_use=True,
# )

# logger = structlog.get_logger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize services

db = MongoDB()
embedding_generator = EmbeddingGenerator()
vector_store = VectorStore()
llm_service = LocalLLMService()  # Changed to LocalLLMService


# Helper decorator for error handling
def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error("API error", error=str(e))
            return jsonify({"error": str(e)}), 500
    return wrapper

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/health', methods=['GET'])
@handle_errors
def health_check():
    return jsonify({"status": "OK"})

@app.route('/documents', methods=['POST'])
@handle_errors
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    # Process text based on file type
    if file.filename.endswith('.txt'):
        content = file.read().decode('utf-8')
    elif file.filename.endswith('.docx'):
        from docx import Document
        doc = Document(file)
        content = "\n".join([p.text for p in doc.paragraphs])
    else:
        return jsonify({"error": "Unsupported file type"}), 400

    # Store content in DB
    document_id = db.insert_document({
        "content": content,
        "metadata": {"filename": file.filename}
    })

    # Generate embedding
    embedding = embedding_generator.generate_embedding(content)
    vector_store.add_document(embedding, document_id)

    return jsonify({
        "document_id": document_id,
        "message": "Document uploaded successfully"
    })

    # data = request.get_json()
    # if not data or 'content' not in data:
    #     return jsonify({"error": "Content is required"}), 400
        
    # # Store document in MongoDB
    # document_id = db.insert_document({
    #     "content": data['content'],
    #     "metadata": data.get('metadata', {})
    # })
    
    # # Generate embedding and add to vector store
    # embedding = embedding_generator.generate_embedding(data['content'])
    # vector_store.add_document(embedding, document_id)
    
    # return jsonify({
    #     "document_id": document_id,
    #     "message": "Document uploaded successfully"
    # })

@app.route('/documents', methods=['GET'])
@handle_errors
def list_documents():
    documents = db.get_all_documents()
    return jsonify(documents)

# @app.route('/query', methods=['POST'])
# @handle_errors
# def handle_query():
#     data = request.get_json()
#     if not data or 'query' not in data:
#         return jsonify({"error": "Query is required"}), 400

#     query = data['query']
    
#     # Generate query embedding using SentenceTransformer
#     query_embedding = embedding_generator.generate_embedding(query)

#     # Search vector store (FAISS) for relevant docs
#     search_results = vector_store.search(query_embedding)
    
#     # Retrieve documents by their IDs from DB or wherever stored
#     context = []
#     for result in search_results:
#         doc = db.get_document(result['document_id'])  # Ensure document is retrieved by correct ID
#         if doc:
#             context.append(doc)
    
#     # Use Mistral LLM for generating a response based on the query and context
#     answer = llm_service.generate_response(query, context)

#     return jsonify({
#         "query": query,
#         "answer": answer,
#         "context_documents": [doc['_id'] for doc in context]
#     })
@app.route('/query', methods=['POST'])
@handle_errors
def handle_query():
    try:
        # Parse incoming JSON data from request
        data = request.get_json()
        if not data or 'query' not in data:
            logger.warning("Query parameter is missing in the request")
            return jsonify({"error": "Query is required"}), 400

        query = data['query']
        logger.info(f"Processing query: {query}")

        # Generate query embedding
        query_embedding = embedding_generator.generate_embedding(query)
        
        # Search vector store (FAISS) for relevant documents
        search_results = vector_store.search(query_embedding)
        logger.info(f"Vector store search returned {len(search_results)} results")
        
        # Retrieve documents by their IDs from DB
        context = []
        missing_docs = []
        
        for result in search_results:
            doc_id = result['document_id']
            try:
                # Try both string and ObjectId formats
                doc = db.get_document(ObjectId(doc_id)) or db.get_document(doc_id)
                
                if not doc:
                    logger.warning(f"Document exists but couldn't load: {doc_id}")
                    continue
                    
                context.append(doc)
            except Exception as e:
                logger.error(f"Document retrieval failed for {doc_id}: {str(e)}")

        if not context:
            logger.warning("No documents found for the query")
            if missing_docs:
                return jsonify({
                    "error": "Relevant documents were found but not available in database",
                    "missing_document_ids": missing_docs
                }), 404
            return jsonify({"error": "No relevant documents found for the query"}), 404
        
        # Generate response
        answer = llm_service.generate_response(query, context)
        
        logger.info(f"Successfully generated response for query: {query}")
        return jsonify({
            "query": query,
            "answer": answer,
            "context_documents": [str(doc['_id']) for doc in context],  # Ensure IDs are strings
        })

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error processing your query"}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)