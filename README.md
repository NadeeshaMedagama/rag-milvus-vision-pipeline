# Python RAG with Milvus & LangGraph

A production-ready Retrieval-Augmented Generation (RAG) application that processes markdown files from GitHub repositories, creates embeddings using Azure OpenAI, and stores them in Milvus Cloud. Built with LangGraph for workflow orchestration and following SOLID principles.

## 🌟 Features

- **📚 GitHub Repository Integration**: Automatically clone and extract all `.md` files from any GitHub repository
- **🌐 URL Content Processing**: Fetch and process content from web URLs including images
- **🖼️ Google Vision API Integration**: Analyze diagrams, images, and visual content with AI-powered computer vision
- **📊 Multi-Format Document Support**: Process 50+ file types including images, diagrams (.drawio, .excalidraw), Word documents (.docx), spreadsheets (.xlsx), PDFs, PowerPoint (.pptx), JSON, Markdown, GraphQL schemas, ODT, and source code files
- **✂️ Intelligent Chunking**: Split documents into manageable chunks with configurable overlap using LangChain
- **🧠 Azure OpenAI Embeddings**: Generate high-quality embeddings using Azure OpenAI's embedding models
- **🗄️ Milvus Cloud Storage**: Efficiently store and retrieve embeddings with vector similarity search
- **🔄 Smart Deduplication**: Automatically skip already-indexed documents to avoid duplicate embeddings and save processing time/costs
- **🏗️ SOLID Architecture**: Clean, maintainable code following all five SOLID principles
- **🔄 LangGraph Workflow**: State machine-based workflow orchestration for robust processing
- **🔍 Interactive Query**: Natural language search interface to query indexed documents
- **⚙️ Fully Configurable**: Environment-based configuration for easy deployment

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Azure OpenAI account with API access
- Milvus Cloud account
- Git

### Installation

```bash
# Navigate to project directory
cd /home/nadeeshame/PycharmProjects/Pythin_RAG_with_Milvus

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Edit `.env` with your credentials:

```bash
# Azure OpenAI
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002

# Milvus Cloud
MILVUS_URI=https://your-instance.cloud.milvus.io:19530
MILVUS_TOKEN=your_token

# GitHub Repository
GITHUB_REPO_URL=https://github.com/langchain-ai/langgraph

# Google Vision API (for diagram/image processing)
GOOGLE_APPLICATION_CREDENTIALS=./credentials/your-credentials.json
PROCESS_LOCAL_FILES=true
DATA_DIRECTORY=./data/diagrams

# URL Processing (optional)
PROCESS_URLS=false
URL_LIST=https://example.com/doc1,https://example.com/doc2
URL_FILE_PATH=./urls.txt

# Processing Control
SKIP_EXISTING_DOCUMENTS=true
FORCE_REPROCESS=false
```

For detailed Google Vision API setup instructions, see [Google Vision Setup Guide](docs/readmes/GOOGLE_VISION_SETUP.md).

### Test Your Setup

```bash
python test_setup.py
```

### Run the Application

1. **Index documents from a GitHub repository:**
   ```bash
   python main.py
   ```

2. **Query the indexed documents:**
   ```bash
   python query.py
   ```

## 📁 Project Structure

```
.
├── config/                      # ⚙️  Configuration management
│   ├── __init__.py
│   └── settings.py             # Pydantic settings from .env
│
├── interfaces/                  # 🔌 Abstract base classes (Interface Segregation)
│   ├── __init__.py
│   └── service_interfaces.py  # IRepositoryReader, IDocumentChunker, etc.
│
├── models/                      # 📦 Data models
│   ├── __init__.py
│   └── data_models.py         # Document, Chunk, EmbeddedChunk, WorkflowState
│
├── services/                    # 🛠️  Service implementations (Single Responsibility)
│   ├── __init__.py
│   ├── repository_reader.py   # GitHub repository operations
│   ├── document_chunker.py    # Document chunking logic
│   ├── embedding_service.py   # Azure OpenAI embeddings
│   ├── vector_store.py        # Milvus vector operations
│   ├── vision_analyzer.py     # Google Vision API image analysis
│   ├── local_file_reader.py   # Local file reading (50+ formats: diagrams, images, docs, code, etc.)
│   └── url_content_reader.py  # URL content fetching and processing
│
├── workflows/                   # 🔄 LangGraph workflows
│   ├── __init__.py
│   └── rag_workflow.py        # RAG pipeline state machine
│
├── data/                        # 📂 Local data directory
│   └── diagrams/               # Architecture diagrams and images
│
├── credentials/                 # 🔐 API credentials (not in git)
│   └── *.json                  # Google Cloud service account keys
│
├── docs/                        # 📚 Documentation
│   ├── ARCHITECTURE.md         # Architecture details
│   ├── SETUP.md                # Setup guide
│   ├── USAGE.md                # Usage guide
│   └── GOOGLE_VISION_SETUP.md  # Google Vision API setup
│
├── main.py                     # 🎯 Main entry point for indexing
├── query.py                    # 🔍 Interactive query interface
├── test_setup.py               # 🧪 Setup verification script
├── requirements.txt            # 📋 Python dependencies
├── .env                        # 🔐 Your configuration (edit this)
├── .env.example                # 📝 Configuration template
├── README.md                   # 📖 This file
├── SETUP.md                    # 🚀 Detailed setup guide
├── USAGE.md                    # 📚 Usage guide
└── ARCHITECTURE.md             # 🏛️  SOLID principles documentation
```

## 🏗️ Architecture

### SOLID Principles Implementation

- **Single Responsibility**: Each service handles one specific task
- **Open/Closed**: Easy to extend with new implementations
- **Liskov Substitution**: All implementations follow their interface contracts
- **Interface Segregation**: Small, focused interfaces
- **Dependency Inversion**: High-level modules depend on abstractions

See [ARCHITECTURE.md](docs/readmes/ARCHITECTURE.md) for detailed architecture documentation.

### Workflow Pipeline

```
┌─────────────────────┐
│  Clone Repository   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│Extract .md Files    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Process Local Files │ ◄── Google Vision API
│ (Diagrams/Images/   │     • Image Analysis
│  PDFs/PowerPoints)  │     • OCR Text Extraction
└──────────┬──────────┘     • Object Detection
           │
           ▼
┌─────────────────────┐
│  Process URLs       │ ◄── HTTP Fetch + Vision API
│ (Web/Image URLs)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Filter Existing     │ ◄── Skip Already Indexed
│    Documents        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Chunk Documents    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Create Embeddings   │ ◄── Azure OpenAI
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Store in Milvus    │ ◄── Vector Database
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│      Cleanup        │
└─────────────────────┘
```

### Supported File Types

| Category | File Types | Processing Method |
|----------|-----------|-------------------|
| **Markdown** | `.md`, `.markdown` | Text extraction with metadata |
| **Images** | `.png`, `.jpg`, `.jpeg`, `.svg`, `.gif`, `.bmp`, `.webp` | Google Vision API analysis |
| **Diagrams** | `.drawio` (+ `.png` exports) | XML parsing + Vision API |
| **Excalidraw** | `.excalidraw` | JSON parsing, text element extraction |
| **Documents** | `.docx` | Text and table extraction |
| **OpenDocument** | `.odt` | Paragraph extraction (odfpy) |
| **Spreadsheets** | `.xlsx`, `.xls` | Data extraction from sheets |
| **PDF** | `.pdf` | Text and table extraction (pdfplumber) |
| **PowerPoint** | `.pptx` | Slide text and table extraction |
| **JSON** | `.json` | Pretty-print with structure analysis |
| **GraphQL** | `.graphql`, `.gql` | Schema extraction with query/mutation detection |
| **Video** | `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm` | Metadata extraction (file size, path) |
| **Text/Config** | `.txt`, `.log`, `.yml`, `.yaml`, `.xml`, `.ini`, `.cfg`, `.conf`, `.env` | Plain text extraction |
| **Source Code** | `.py`, `.js`, `.ts`, `.java`, `.go`, `.rs`, `.c`, `.cpp`, `.h`, `.sh`, `.sql`, `.html`, `.css` | Code content extraction |
| **URLs** | Web pages, images | HTTP fetch + Vision API for images |

## 📖 Documentation

- **[SETUP.md](docs/readmes/SETUP.md)** - Detailed setup instructions
- **[USAGE.md](docs/readmes/USAGE.md)** - Usage guide with examples
- **[ARCHITECTURE.md](docs/readmes/ARCHITECTURE.md)** - SOLID principles and architecture details

## 🔧 Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `CHUNK_SIZE` | Size of text chunks | 1000 |
| `CHUNK_OVERLAP` | Overlap between chunks | 200 |
| `EMBEDDING_DIMENSION` | Vector dimension | 1536 |
| `MILVUS_COLLECTION_NAME` | Collection name | readme_embeddings |
| `PROCESS_LOCAL_FILES` | Enable local file processing | true |
| `DATA_DIRECTORY` | Directory for local files | ./data/diagrams |
| `PROCESS_URLS` | Enable URL content processing | false |
| `URL_LIST` | Comma-separated URLs to process | "" |
| `URL_FILE_PATH` | Path to file containing URLs | "" |
| `URL_TIMEOUT` | Timeout for URL fetching (seconds) | 30 |
| `SKIP_EXISTING_DOCUMENTS` | Skip already indexed documents | true |
| `FORCE_REPROCESS` | Force reprocess all documents | false |

## 💡 Example Usage

```python
# Programmatic usage
from config import get_settings
from services import *
from workflows import RAGWorkflow

settings = get_settings()

# Initialize services
workflow = RAGWorkflow(
    repository_reader=GitHubRepositoryReader(),
    document_chunker=DocumentChunker(),
    embedding_service=AzureOpenAIEmbeddingService(...),
    vector_store=MilvusVectorStore(...)
)

# Process repository
workflow.run("https://github.com/user/repo")
```

## 🤝 Contributing

This project follows SOLID principles and clean code practices. When contributing:
1. Follow the existing architecture patterns
2. Implement interfaces for new services
3. Add proper documentation
4. Test your changes

## 📄 License

This project is provided as-is for educational and commercial use.

## 🙏 Acknowledgments

- LangGraph for workflow orchestration
- LangChain for document processing
- Azure OpenAI for embeddings
- Milvus for vector storage

