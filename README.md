# RAG
# 🧠 RAG System with Flask & HTML Frontend

This project is a **Retrieval-Augmented Generation (RAG)** system built with:

- 🐍 Flask (Python backend)
- 🧾 Vanilla HTML + JavaScript frontend (simple ui)
- 📄 Text file upload for building the knowledge base
- 🤖 Query endpoint to perform retrieval and generation over uploaded documents
-    used the together ai api key to get the response from the model
---

## ⚙️ Features

- 📤 Upload `.txt` files via the browser
- 🧠 Query the uploaded knowledge using a `/query` endpoint
- 📚 View uploaded documents with `/documents`
- 💓 Check system status with `/health`

---

## 📁 Project Structure

├── app.py                # Flask application
├── templates/
│   └── upload.html       # Frontend interface
├── utils/
│   ├── database.py       # MongoDB interactions
│   ├── embeddings.py     # Text embedding generation
│   └── llm.py            # LLM integration
│   └── vector_store.py   # vector integration
├── .env                  # Environment configuration
└── requirements.txt      # Python dependencies

---

## 🚀 Getting Started

### 1. Install Requirements

```bash
pip install -r requirements.txt

python app.py
Then visit:
📍 http://localhost:5000



🔐 API Endpoints
Endpoint	    Method	Description
/api/documents	POST	Upload document
/api/documents	GET	    List documents
/api/query	   POST	    Submit query


📤 POST /documents
Uploads a .txt file to the server.

Request: Form-data with key file

Response:


{
  "message": "File uploaded successfully",
  "filename": "example.txt"
}
📄 GET /documents
Returns a list of uploaded documents.

Response:


{
  "documents": ["doc1.txt", "doc2.txt"]
}
GET /health
Checks if the backend is running.

Response:

{
  "status": "OK"
}
