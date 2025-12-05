# Usage Guide

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   - Copy `.env.example` to `.env`
   - Fill in your Azure OpenAI credentials
   - Fill in your Milvus Cloud credentials
   - Set your GitHub repository URL
   - Add Google Vision API credentials (for diagram/image processing)

3. **Google Vision API Setup** (Optional - for diagram processing):
   - Create a Google Cloud Project
   - Enable the Vision API
   - Create a service account and download the JSON credentials
   - Place the credentials file in the `credentials/` directory
   - Update `GOOGLE_APPLICATION_CREDENTIALS` in `.env` with the path

## Running the Application

### 1. Process and Index Documents

Run the main script to clone a repository, chunk markdown files, process diagrams/images, create embeddings, and store them in Milvus:

```bash
python main.py
```

This will:
1. Clone the specified GitHub repository
2. Extract all `.md` files
3. **Process local diagrams and images** (if enabled):
   - Scan the data directory for images (.png, .jpg, .svg, etc.)
   - Analyze diagrams (.drawio files and exports)
   - Extract text from Word documents (.docx)
   - Process spreadsheets (.xlsx)
   - Use Google Vision API to generate comprehensive summaries
4. Chunk the documents
5. Create embeddings using Azure OpenAI
6. Store embeddings in Milvus Cloud
7. Clean up temporary files

### 2. Query the System

After indexing, you can query the system:

```bash
python query.py
```

This starts an interactive query interface where you can:
- Enter natural language queries
- Get relevant document chunks
- See similarity scores
- View source file paths

Example queries:
- "How do I install this library?"
- "What are the main features?"
- "Show me the API documentation"

## Configuration Options

### .env File

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key | `abc123...` |
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI endpoint | `https://your-resource.openai.azure.com/` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Deployment name for chat | `gpt-4` |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Deployment name for embeddings | `text-embedding-ada-002` |
| `MILVUS_URI` | Milvus Cloud URI | `https://your-instance.cloud.milvus.io:19530` |
| `MILVUS_TOKEN` | Milvus Cloud token | `your_token` |
| `MILVUS_COLLECTION_NAME` | Collection name | `readme_embeddings` |
| `GITHUB_REPO_URL` | Repository to process | `https://github.com/user/repo` |
| `GITHUB_TOKEN` | Optional GitHub token | Leave empty for public repos |
| `CHUNK_SIZE` | Size of text chunks | `1000` |
| `CHUNK_OVERLAP` | Overlap between chunks | `200` |
| `EMBEDDING_DIMENSION` | Embedding vector dimension | `1536` (for ada-002) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Google Vision API credentials | `./credentials/your-credentials.json` |
| `GOOGLE_VISION_MAX_RESULTS` | Max results from Vision API | `10` |
| `DATA_DIRECTORY` | Path to local data directory | `./data/diagrams` |
| `PROCESS_LOCAL_FILES` | Enable local file processing | `true` or `false` |

## Supported File Types

The system now supports multiple file types:

### Images and Diagrams
- **Images**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.svg`, `.webp`
  - Analyzed using Google Vision API
  - Extracts text, labels, objects, and logos
  - Generates comprehensive descriptions

- **Diagrams**: `.drawio`
  - Reads XML content
  - If `.png` export exists, also analyzes visually
  - Combines text and visual analysis

### Documents
- **Word Documents**: `.docx`
  - Extracts paragraphs and tables
  - Preserves document structure

### Data Files
- **Spreadsheets**: `.xlsx`, `.xls`
  - Extracts data from all sheets
  - Includes cell values and structure

## Advanced Usage

### Processing Multiple Repositories

You can modify `main.py` to process multiple repositories:

```python
repositories = [
    "https://github.com/user/repo1",
    "https://github.com/user/repo2",
]

for repo_url in repositories:
    final_state = workflow.run(repo_url)
```

### Custom Chunking Strategy

Modify the chunking parameters in `.env`:

```env
CHUNK_SIZE=500          # Smaller chunks for more granular search
CHUNK_OVERLAP=100       # Less overlap for more distinct chunks
```

### Different Embedding Models

You can use different Azure OpenAI embedding models by changing:

```env
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
EMBEDDING_DIMENSION=3072  # Adjust based on model
```

### Programmatic Query

You can also use the query service programmatically:

```python
from config import get_settings
from services import AzureOpenAIEmbeddingService, MilvusVectorStore
from query import RAGQueryService

settings = get_settings()

# Initialize services
embedding_service = AzureOpenAIEmbeddingService(...)
vector_store = MilvusVectorStore(...)
query_service = RAGQueryService(embedding_service, vector_store)

# Query
results = query_service.query("How to use this?", top_k=3)
for result in results:
    print(result['content'])
```

## Troubleshooting

### Connection Issues

If you can't connect to Milvus Cloud:
- Verify your `MILVUS_URI` includes the port (usually :19530)
- Check that your `MILVUS_TOKEN` is correct
- Ensure your IP is whitelisted in Milvus Cloud settings

### Azure OpenAI Errors

If you get authentication errors:
- Verify your `AZURE_OPENAI_API_KEY` is correct
- Check that your deployment names match your Azure setup
- Ensure your endpoint URL is correct

### GitHub Cloning Issues

If repository cloning fails:
- Check your internet connection
- For private repos, provide a `GITHUB_TOKEN`
- Ensure the repository URL is correct

### Memory Issues

For large repositories:
- Process in batches by modifying the workflow
- Increase chunk size to reduce number of chunks
- Use a machine with more RAM

