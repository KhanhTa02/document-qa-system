# Document Q&A System

A RAG-based question answering system for PDF documents using LangChain, Unstructured, ChromaDB, and Ollama.

## Features

- PDF document processing with Unstructured
- Vector storage with ChromaDB
- Hybrid retrieval (vector + BM25)
- Sub-question generation for complex queries
- Page number source citation
- Multilingual query supports
- Fully local

## Setup

1. Install Ollama models:
```bash
ollama pull llama3.1
ollama pull nomic-embed-text
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the web app:
```bash
python flask_frontend.py
```

4. Open http://localhost:5001

## Usage

### Web Interface
- Upload your PDF to the `source_documents` folder
- The system will automatically detect and use the first PDF file found
- Ask questions through the web interface

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PDF Document  │───▶│  Text Chunking  │───▶│  Vector Storage │
│                 │    │  (Unstructured) │    │  (ChromaDB)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Question │───▶│ Sub-Question    │───▶│  Hybrid         │
│                 │    │ Generation      │    │  Retrieval      │
│                 │    │ (Complexity     │    │  (Vector +      │
│                 │    │  Analysis)      │    │   BM25)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Page Numbers   │◀───│  Response       │◀───│  Reranking &    │
│  as Sources     │    │  Synthesis      │    │  QA Chain       │
│                 │    │  (LLM)          │    │  (Context       │
│                 │    │                 │    │   Assembly)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Files

- `rag_backend.py` - Main RAG system
- `flask_frontend.py` - Web interface
- `requirements.txt` - Dependencies
- `templates/` - HTML templates
- `static/` - CSS/JS assets
- `source_documents/` - PDF storage folder
- `chroma_db/` - Vector database storage 