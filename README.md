# Python RAG with Milvus & LangGraph

[![CI/CD Pipeline](https://github.com/YOUR_USERNAME/Pythin_RAG_with_Milvus/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/Pythin_RAG_with_Milvus/actions/workflows/ci.yml)
[![CodeQL](https://github.com/YOUR_USERNAME/Pythin_RAG_with_Milvus/actions/workflows/codeql.yml/badge.svg)](https://github.com/YOUR_USERNAME/Pythin_RAG_with_Milvus/actions/workflows/codeql.yml)
[![Docker Build](https://github.com/YOUR_USERNAME/Pythin_RAG_with_Milvus/actions/workflows/docker.yml/badge.svg)](https://github.com/YOUR_USERNAME/Pythin_RAG_with_Milvus/actions/workflows/docker.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)

A production-ready Retrieval-Augmented Generation (RAG) application that processes markdown files from GitHub repositories, creates embeddings using Azure OpenAI, and stores them in Milvus Cloud. Built with LangGraph for workflow orchestration and following SOLID principles.

## 🌟 Features

- **📚 GitHub Repository Integration**: Automatically clone and extract all `.md` files from any GitHub repository
- **🌐 URL Content Processing**: Fetch and process content from web URLs including images
- **🔗 Automatic URL Extraction**: Detect and process URLs found within document content (PDFs, Word docs, etc.)
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

# URL Extraction from Document Content (enabled by default)
EXTRACT_URLS_FROM_CONTENT=true

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

## 🚢 Docker Deployment

### Pull Pre-built Image

```bash
# Option 1: Pull from Docker Hub
docker pull YOUR_DOCKERHUB_USERNAME/rag-milvus-vision-pipeline:latest

# Option 2: Pull from GitHub Container Registry
docker pull ghcr.io/YOUR_USERNAME/rag-milvus-vision-pipeline:latest

# Run the container
docker run -d -p 5000:5000 \
  --name rag-api \
  -e AZURE_OPENAI_API_KEY=your_key \
  -e AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/ \
  -e MILVUS_URI=https://your-instance.cloud.milvus.io:19530 \
  -e MILVUS_TOKEN=your_token \
  YOUR_DOCKERHUB_USERNAME/rag-milvus-vision-pipeline:latest
```

### Build Locally

```bash
# Build the Docker image
docker build -t python-rag-milvus:local .

# Run the container
docker run -d -p 5000:5000 \
  --name rag-api \
  --env-file .env \
  python-rag-milvus:local

# Check health
curl http://localhost:5000/health
```

### API Endpoints

- **Health Check**: `GET /health`
- **Query**: `POST /api/query`
  ```json
  {
    "query": "How do I configure Milvus?",
    "top_k": 5
  }
  ```

## 🔄 CI/CD Pipeline

This project includes a comprehensive CI/CD pipeline using GitHub Actions that provides:

### Automated Workflows

#### 1. **CI/CD Pipeline** (`.github/workflows/ci.yml`)
Runs on every push and pull request to `main` and `develop` branches.

**Features:**
- ✅ Code quality checks (Black, isort, flake8, pylint)
- 🔍 Type checking with mypy
- 🛡️ Security scanning with Bandit
- 🧪 Automated testing with pytest and coverage reporting
- 📊 Coverage reports uploaded to Codecov
- 🐳 Docker image build and testing
- 🔒 Container vulnerability scanning with Trivy

#### 2. **CodeQL Security Analysis** (`.github/workflows/codeql.yml`)
Runs weekly and on every push/PR.

**Features:**
- 🔐 Advanced security vulnerability detection
- 📈 Code quality analysis
- 🎯 Python-specific security patterns
- 📊 Results uploaded to GitHub Security tab
- ⏰ Scheduled weekly scans (Mondays at 6:00 AM UTC)

#### 3. **Docker Build & Publish** (`.github/workflows/docker.yml`)
Runs on main branch pushes and version tags.

**Features:**
- 🐳 Multi-platform builds (linux/amd64, linux/arm64)
- 📦 Publishes to **Docker Hub** and GitHub Container Registry (ghcr.io)
- 🏷️ Semantic versioning with tags
- 🔒 Image vulnerability scanning with Trivy
- 📋 SBOM (Software Bill of Materials) generation
- 💾 Build cache optimization

**Required Secrets:**
- `DOCKER_USERNAME` - Your Docker Hub username
- `DOCKER_PASSWORD` - Your Docker Hub password or access token

#### 4. **Release Management** (`.github/workflows/release.yml`)
Triggered on version tags (v*.*.*) or manual dispatch.

**Features:**
- 📝 Automated changelog generation
- 🎉 GitHub Release creation
- 📦 Source distribution packaging
- 🐳 Docker image tagging
- 📊 Release notes with categorized changes

#### 5. **Dependency Updates** (`.github/workflows/dependency-check.yml`)
Runs weekly and on dependency file changes.

**Features:**
- 📦 Checks for outdated Python packages
- 🔒 Security vulnerability audits with pip-audit
- 📄 License compliance reporting
- 🐳 Docker base image update checks
- 🔄 GitHub Actions version tracking

#### 6. **Dependabot Configuration** (`.github/dependabot.yml`)
Automated dependency updates.

**Features:**
- 🔄 Weekly automated dependency updates
- 🐍 Python package updates (grouped by category)
- 🐳 Docker base image updates
- ⚙️ GitHub Actions workflow updates
- 🤖 Auto-merge for patch updates

### Setting Up CI/CD

1. **Enable GitHub Actions** in your repository settings

2. **Configure Secrets** (Settings → Secrets and variables → Actions):
   - `GITHUB_TOKEN` is automatically provided
   - `DOCKER_USERNAME` - Your Docker Hub username
   - `DOCKER_PASSWORD` - Your Docker Hub password or access token
   - Add any additional secrets needed for your deployment

3. **Enable GitHub Container Registry**:
   - Go to repository Settings → Actions → General
   - Under "Workflow permissions", select "Read and write permissions"

4. **Enable Security Features**:
   - Go to Settings → Security → Code security and analysis
   - Enable "Dependency graph" (required for dependency review)
   - Enable "Dependabot alerts"
   - Enable "Dependabot security updates"
   - Enable "CodeQL analysis"

5. **Update Badge URLs** in README.md:
   - Replace `YOUR_USERNAME` with your GitHub username
   - Replace `YOUR_DOCKERHUB_USERNAME` with your Docker Hub username

### Workflow Triggers

| Workflow | Push | PR | Tag | Schedule | Manual | Auto-Trigger Files |
|----------|------|-----|-----|----------|--------|-------------------|
| CI/CD Pipeline | ✅ main/develop | ✅ | ❌ | ❌ | ✅ | `*.py`, `requirements.txt`, `Dockerfile`, `.github/workflows/**` |
| CodeQL Analysis | ✅ main/develop | ✅ | ❌ | ✅ Weekly | ✅ | `*.py`, `requirements.txt` |
| Docker Build | ✅ main | ✅ | ✅ | ❌ | ✅ | `*.py`, `requirements.txt`, `Dockerfile` |
| Release | ❌ | ❌ | ✅ v*.*.* | ❌ | ✅ | N/A |
| Dependency Check | ✅ main/develop | ✅ deps | ❌ | ✅ Weekly | ✅ | `requirements.txt`, `pyproject.toml`, `Dockerfile` |

### Creating a Release

To create a new release:

```bash
# Tag the release
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push the tag to GitHub
git push origin v1.0.0
```

This will automatically:
1. Trigger the Release workflow
2. Build and push Docker images with version tags
3. Generate changelog from commit history
4. Create a GitHub Release with artifacts
5. Publish to GitHub Container Registry

### Monitoring

- **Workflow runs**: Check the "Actions" tab in your repository
- **Security alerts**: Check the "Security" tab for CodeQL and Trivy results
- **Coverage reports**: Uploaded as artifacts in workflow runs
- **Docker images**: Available at `ghcr.io/YOUR_USERNAME/pythin_rag_with_milvus`

## 📁 Project Structure

```
.
├── .github/                     # 🔄 CI/CD Configuration
│   ├── workflows/
│   │   ├── ci.yml              # Main CI/CD pipeline
│   │   ├── codeql.yml          # Security analysis
│   │   ├── docker.yml          # Docker build & publish
│   │   ├── release.yml         # Release management
│   │   ├── dependency-check.yml # Dependency auditing
│   │   └── dependabot-auto-merge.yml # Auto-merge bot
│   └── dependabot.yml          # Dependabot configuration
│
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
├── api_server.py               # 🌐 REST API server
├── test_setup.py               # 🧪 Setup verification script
├── requirements.txt            # 📋 Python dependencies
├── Dockerfile                  # 🐳 Container configuration
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
│ Extract URLs from   │ ◄── Scan Document Content
│ Document Content    │     • Find embedded URLs
│ (PDFs/Docs/etc.)    │     • Fetch URL content
└──────────┬──────────┘     • Add to documents
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
| `EXTRACT_URLS_FROM_CONTENT` | Extract and process URLs from document content | true |
| `SKIP_EXISTING_DOCUMENTS` | Skip already indexed documents | true |
| `FORCE_REPROCESS` | Force reprocess all documents | false |

## 🔗 Automatic URL Extraction from Document Content

The application can automatically detect and process URLs found within your document content. This is especially useful when:

- **PDFs contain reference links** to external documentation
- **Word documents have embedded URLs** to related resources
- **Markdown files link to external content** you want to index

### How It Works

1. **During processing**, the workflow scans all document content for URLs
2. **URLs are extracted** using pattern matching (http/https links, markdown links, etc.)
3. **Each URL is fetched** and its content is processed
4. **Content is added** to the vector database alongside the original documents

### Configuration

```bash
# Enable/disable URL extraction (enabled by default)
EXTRACT_URLS_FROM_CONTENT=true
```

### Example

If your PDF contains text like:
```
For more information, see https://docs.example.com/api-reference
```

The system will:
1. Extract the URL `https://docs.example.com/api-reference`
2. Fetch the content from that URL
3. Store the URL's content in Milvus
4. Link it back to the original document that contained the URL

### Supported URL Types

| URL Type | Processing |
|----------|------------|
| Web pages (HTML) | Text extraction with BeautifulSoup |
| Images | Google Vision API analysis |
| JSON APIs | JSON content indexing |
| Plain text/Markdown | Direct text extraction |

## 🔄 Incremental Processing

The application supports **smart incremental processing** to avoid reprocessing files that have already been indexed in the vector store. This saves time and API costs.

### How It Works

1. **On startup**, the workflow queries the Milvus collection for all existing file paths
2. **When scanning files**, both local files and GitHub repository files are checked against the existing paths
3. **Files that already exist** are automatically skipped
4. **Only new files** are processed, chunked, and embedded

### Configuration

```bash
# Recommended: Enable incremental processing (default)
SKIP_EXISTING_DOCUMENTS=true
FORCE_REPROCESS=false

# Full reindex: Process all files again
SKIP_EXISTING_DOCUMENTS=false
FORCE_REPROCESS=true
```

### Processing Modes

| Mode | `SKIP_EXISTING_DOCUMENTS` | `FORCE_REPROCESS` | Behavior |
|------|---------------------------|-------------------|----------|
| **Incremental** ✅ | `true` | `false` | Only new files are processed (fastest) |
| **Full Reindex** | `false` | `true` | All files reprocessed, collection recreated |
| **Add Only** | `true` | `true` | Force ignores skip (processes all) |

### Output Example

```
📊 Document Status:
  - Total found: 150
  - Already indexed: 145
  - New to process: 5

✅ All documents already indexed. Nothing to process!
💡 Tip: Use FORCE_REPROCESS=true in .env to reprocess all documents
```

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

