# Setup Guide

## Quick Start

### 1. Prerequisites
- Python 3.8 or higher
- Azure OpenAI account and API credentials
- Milvus Cloud account
- Git installed

### 2. Installation

```bash
# Navigate to project directory
cd /home/nadeeshame/PycharmProjects/Pythin_RAG_with_Milvus

# Activate virtual environment (if not already active)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Edit the `.env` file with your actual credentials:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_actual_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002

# Milvus Cloud Configuration
MILVUS_URI=https://your-instance.cloud.milvus.io:19530
MILVUS_TOKEN=your_milvus_token_here
MILVUS_COLLECTION_NAME=readme_embeddings

# GitHub Repository Configuration
GITHUB_REPO_URL=https://github.com/langchain-ai/langgraph
GITHUB_TOKEN=  # Leave empty for public repos

# Application Configuration (defaults are fine)
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EMBEDDING_DIMENSION=1536
```

### 4. Run the Application

#### Process and Index Documents

```bash
python main.py
```

This will:
1. Clone the GitHub repository
2. Extract all `.md` files
3. Chunk the documents
4. Create embeddings using Azure OpenAI
5. Store embeddings in Milvus Cloud

#### Query the System

After indexing, query the system:

```bash
python query.py
```

Enter your natural language queries when prompted.

## Project Structure

```
.
├── config/                      # Configuration management
│   ├── __init__.py
│   └── settings.py             # Settings from .env
├── interfaces/                  # Abstract base classes (SOLID - ISP)
│   ├── __init__.py
│   └── service_interfaces.py  # Service interfaces
├── models/                      # Data models
│   ├── __init__.py
│   └── data_models.py         # Document, Chunk, EmbeddedChunk
├── services/                    # Service implementations (SOLID - SRP)
│   ├── __init__.py
│   ├── document_chunker.py    # Document chunking service
│   ├── embedding_service.py   # Azure OpenAI embedding service
│   ├── repository_reader.py   # GitHub repository reader
│   └── vector_store.py        # Milvus vector store service
├── workflows/                   # LangGraph workflows
│   ├── __init__.py
│   └── rag_workflow.py        # RAG workflow orchestration
├── main.py                     # Main entry point for indexing
├── query.py                    # Query interface for searching
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (you edit this)
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore file
├── README.md                   # Project documentation
├── ARCHITECTURE.md             # SOLID principles documentation
└── USAGE.md                    # Usage guide
```

## Key Features

### SOLID Principles
- **Single Responsibility**: Each class has one job
- **Open/Closed**: Extensible without modification
- **Liskov Substitution**: Interfaces are substitutable
- **Interface Segregation**: Small, focused interfaces
- **Dependency Inversion**: Depend on abstractions

### LangGraph Workflow
The application uses LangGraph to orchestrate the RAG pipeline as a state machine with clear steps.

### Azure OpenAI Integration
Uses Azure OpenAI for generating embeddings with proper error handling and batch processing.

### Milvus Cloud Storage
Efficient vector storage and similarity search using Milvus Cloud.

## Troubleshooting

### Missing Dependencies
If you get import errors:
```bash
pip install -r requirements.txt
```

### Configuration Errors
Make sure all required variables in `.env` are filled in.

### Connection Issues
- **Milvus**: Check URI and token
- **Azure OpenAI**: Verify endpoint and API key
- **GitHub**: Ensure repository URL is correct

## Next Steps

1. **Edit `.env`** with your credentials
2. **Run `python main.py`** to index documents
3. **Run `python query.py`** to search

See `USAGE.md` for advanced usage and `ARCHITECTURE.md` for architecture details.

