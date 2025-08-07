# Document Q&A System

A production-ready RAG-based question answering system for PDF documents using LangChain, Unstructured, ChromaDB, and Ollama. This system demonstrates advanced NLP techniques including hybrid retrieval, sub-question generation, and source citation.

## Technical Stack

- **Backend**: Python, Flask, LangChain
- **Vector Database**: ChromaDB with hybrid retrieval (vector + BM25)
- **Document Processing**: Unstructured for PDF parsing
- **Language Models**: Ollama (llama3.1 for generation, nomic-embed-text for embeddings)
- **Frontend**: HTML, CSS, JavaScript with modern UI
- **Architecture**: Modular design with separation of concerns

## Key Features

- **Advanced RAG Pipeline**: Implements retrieval-augmented generation with context-aware responses
- **Hybrid Retrieval**: Combines vector similarity and BM25 for improved search accuracy
- **Sub-Question Generation**: Automatically breaks down complex queries into simpler sub-questions
- **Source Citation**: Provides page numbers and document references for all responses
- **Multilingual Support**: Handles queries in multiple languages
- **Fully Local**: No external API dependencies, ensuring data privacy
- **Modern Web Interface**: Clean, responsive UI with real-time interaction

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
│                 │    │ (LLM)           │    │ (Context        │
│                 │    │                 │    │  Assembly)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Implementation Highlights

### 1. Document Processing Pipeline
- Automatic PDF parsing with Unstructured library
- Intelligent text chunking with overlap for context preservation
- Metadata extraction for source tracking

### 2. Advanced Retrieval System
- Dual retrieval strategy: semantic similarity + keyword matching
- Dynamic reranking based on query complexity
- Context window optimization for large documents

### 3. Query Processing
- Automatic query classification and complexity analysis
- Sub-question generation for complex multi-part queries
- Query expansion and refinement

### 4. Response Generation
- Context-aware answer synthesis
- Source citation with page numbers
- Confidence scoring for responses

## Quick Start

### Prerequisites
- Python 3.8+
- Ollama installed and running

### Installation

1. **Install Ollama models:**
```bash
ollama pull llama3.1
ollama pull nomic-embed-text
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Start the application:**
```bash
python flask_frontend.py
```

4. **Access the web interface:**
   - Open http://localhost:5001
   - Upload your PDF to the `source_documents` folder
   - The system automatically processes and indexes the document

## Usage

### Web Interface
- **Document Upload**: Place PDF files in the `source_documents` folder
- **Query Interface**: Ask questions in natural language
- **Response Display**: View answers with source citations
- **Real-time Processing**: Immediate feedback and response generation

### API Endpoints
- `POST /upload` - Document upload and processing
- `POST /query` - Question answering endpoint
- `GET /status` - System status and health check

## Project Structure

```
├── rag_backend.py          # Core RAG implementation
├── flask_frontend.py       # Web application server
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── templates/
│   └── index.html         # Main web interface
├── static/
│   ├── css/
│   │   └── style.css      # Styling and UI components
│   ├── js/
│   │   └── app.js         # Frontend JavaScript logic
│   └── images/            # UI assets
└── source_documents/      # PDF storage directory
```

## Technical Implementation Details

### RAG Pipeline Components
1. **Document Ingestion**: PDF parsing with Unstructured
2. **Text Chunking**: Semantic-aware splitting with overlap
3. **Embedding Generation**: Using nomic-embed-text model
4. **Vector Storage**: ChromaDB with metadata indexing
5. **Query Processing**: Sub-question generation and expansion
6. **Retrieval**: Hybrid vector + BM25 search
7. **Response Generation**: Context-aware LLM synthesis

### Performance Optimizations
- Efficient vector storage with ChromaDB
- Caching for repeated queries
- Optimized chunk sizes for context preservation
- Asynchronous processing for large documents

## Future Enhancements

- **Multi-document Support**: Handle multiple PDFs simultaneously
- **Advanced Caching**: Redis integration for improved performance
- **User Authentication**: Secure access control
- **API Rate Limiting**: Production-ready request handling
- **Monitoring**: Logging and analytics integration
- **Docker Support**: Containerized deployment

## Contributing

This project demonstrates modern NLP techniques and production-ready code practices. The modular architecture allows for easy extension and modification of individual components. 