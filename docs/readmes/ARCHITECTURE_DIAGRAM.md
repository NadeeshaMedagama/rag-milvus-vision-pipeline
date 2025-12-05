# Project Architecture - With Google Vision API Integration

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                               │
│                    (main.py / query.py)                              │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         RAG WORKFLOW                                 │
│                    (workflows/rag_workflow.py)                       │
│                                                                       │
│  ┌──────────────┐  ┌────────────────┐  ┌──────────────────┐        │
│  │   Clone      │→ │Extract Markdown│→ │Process Local Files│        │
│  │ Repository   │  │     Files      │  │   ← NEW STEP     │        │
│  └──────────────┘  └────────────────┘  └──────────────────┘        │
│                                                  │                    │
│                                                  ▼                    │
│  ┌──────────────┐  ┌────────────────┐  ┌──────────────────┐        │
│  │   Cleanup    │← │Store Embeddings│← │Create Embeddings │        │
│  └──────────────┘  └────────────────┘  └──────────────────┘        │
│                             ▲                    ▲                    │
│                             │                    │                    │
└─────────────────────────────┼────────────────────┼───────────────────┘
                              │                    │
                              │                    │
┌─────────────────────────────┼────────────────────┼───────────────────┐
│                        SERVICE LAYER                                  │
│                   (Following SOLID Principles)                        │
│                                                                       │
│  ┌──────────────────────┐  ┌──────────────────────┐                 │
│  │ IRepositoryReader    │  │ ILocalFileReader      │  ← NEW         │
│  ├──────────────────────┤  ├──────────────────────┤                 │
│  │ GitHubRepositoryReader│ │ LocalFileReader      │                 │
│  └──────────────────────┘  └──────────────────────┘                 │
│              │                        │                               │
│              │                        ▼                               │
│              │              ┌──────────────────────┐                 │
│              │              │ IVisionAnalyzer      │  ← NEW         │
│              │              ├──────────────────────┤                 │
│              │              │ GoogleVisionAnalyzer │                 │
│              │              └──────────────────────┘                 │
│              │                        │                               │
│              ▼                        ▼                               │
│  ┌─────────────────────────────────────────────────┐                │
│  │          IDocumentChunker                        │                │
│  ├─────────────────────────────────────────────────┤                │
│  │          DocumentChunker                         │                │
│  └─────────────────────────────────────────────────┘                │
│                              │                                        │
│                              ▼                                        │
│  ┌─────────────────────────────────────────────────┐                │
│  │        IEmbeddingService                         │                │
│  ├─────────────────────────────────────────────────┤                │
│  │     AzureOpenAIEmbeddingService                  │                │
│  └─────────────────────────────────────────────────┘                │
│                              │                                        │
│                              ▼                                        │
│  ┌─────────────────────────────────────────────────┐                │
│  │          IVectorStore                            │                │
│  ├─────────────────────────────────────────────────┤                │
│  │          MilvusVectorStore                       │                │
│  └─────────────────────────────────────────────────┘                │
│                              │                                        │
└──────────────────────────────┼───────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                                 │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐          │
│  │   GitHub     │  │Azure OpenAI  │  │ Google Vision API│  ← NEW   │
│  │  Repository  │  │  Embeddings  │  │   (OCR, Labels)  │          │
│  └──────────────┘  └──────────────┘  └──────────────────┘          │
│                                                                       │
│  ┌─────────────────────────────────────┐                            │
│  │      Milvus Cloud                    │                            │
│  │   (Vector Database Storage)          │                            │
│  └─────────────────────────────────────┘                            │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌─────────────────┐
│  GitHub Repo    │
│  (.md files)    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              Document Collection                         │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Markdown    │  │   Images     │  │   Diagrams   │  │
│  │   Files      │  │ (.png, .jpg) │  │  (.drawio)   │  │
│  └──────────────┘  └──────┬───────┘  └──────┬───────┘  │
│                            │                  │          │
│  ┌──────────────┐  ┌──────▼───────┐  ┌──────▼───────┐  │
│  │    Word      │  │ Google Vision│  │ Google Vision│  │
│  │ Docs (.docx) │  │     API      │  │     API      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
            ┌──────────────────┐
            │   Raw Documents   │
            │  (with metadata)  │
            └────────┬──────────┘
                     │
                     ▼
            ┌──────────────────┐
            │  Document Chunks  │
            │   (1000 chars)    │
            └────────┬──────────┘
                     │
                     ▼
            ┌──────────────────┐
            │ Azure OpenAI API  │
            │   (Embeddings)    │
            └────────┬──────────┘
                     │
                     ▼
            ┌──────────────────┐
            │ Vector Embeddings │
            │   (1536 dims)     │
            └────────┬──────────┘
                     │
                     ▼
            ┌──────────────────┐
            │  Milvus Cloud DB  │
            │  (Vector Store)   │
            └──────────────────┘
```

## File Type Processing Matrix

```
┌──────────────────┬─────────────────┬──────────────────────┬─────────────┐
│   File Type      │   Extensions    │   Processing Method  │   New?      │
├──────────────────┼─────────────────┼──────────────────────┼─────────────┤
│ Markdown         │ .md             │ Text extraction      │ Existing    │
├──────────────────┼─────────────────┼──────────────────────┼─────────────┤
│ Images           │ .png, .jpg,     │ Google Vision API    │ ✅ NEW      │
│                  │ .jpeg, .svg,    │ - Label detection    │             │
│                  │ .gif, .bmp      │ - OCR                │             │
│                  │                 │ - Object detection   │             │
├──────────────────┼─────────────────┼──────────────────────┼─────────────┤
│ Diagrams         │ .drawio         │ XML parsing +        │ ✅ NEW      │
│                  │ .drawio.png     │ Vision API           │             │
├──────────────────┼─────────────────┼──────────────────────┼─────────────┤
│ Word Documents   │ .docx           │ python-docx          │ ✅ NEW      │
│                  │                 │ - Paragraphs         │             │
│                  │                 │ - Tables             │             │
├──────────────────┼─────────────────┼──────────────────────┼─────────────┤
│ Spreadsheets     │ .xlsx, .xls     │ openpyxl             │ ✅ NEW      │
│                  │                 │ - All sheets         │             │
│                  │                 │ - Cell values        │             │
└──────────────────┴─────────────────┴──────────────────────┴─────────────┘
```

## SOLID Principles in Practice

```
┌─────────────────────────────────────────────────────────────────┐
│  S - Single Responsibility Principle                            │
│  ────────────────────────────────────────────────────────────   │
│  ✅ GoogleVisionAnalyzer     → Only handles Vision API          │
│  ✅ LocalFileReader          → Only handles file reading        │
│  ✅ DocumentChunker          → Only handles chunking            │
│  ✅ EmbeddingService         → Only handles embeddings          │
│  ✅ VectorStore              → Only handles storage             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  O - Open/Closed Principle                                       │
│  ────────────────────────────────────────────────────────────   │
│  ✅ Open for extension: Can add new file types                  │
│  ✅ Closed for modification: No changes to existing services    │
│  ✅ Example: Add PDF support without modifying vision analyzer  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  L - Liskov Substitution Principle                              │
│  ────────────────────────────────────────────────────────────   │
│  ✅ GoogleVisionAnalyzer can be replaced with any               │
│     IVisionAnalyzer implementation                              │
│  ✅ LocalFileReader can be replaced with any                    │
│     ILocalFileReader implementation                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  I - Interface Segregation Principle                            │
│  ────────────────────────────────────────────────────────────   │
│  ✅ IVisionAnalyzer    → 3 focused methods                      │
│  ✅ ILocalFileReader   → 2 focused methods                      │
│  ✅ IDocumentChunker   → 2 focused methods                      │
│  ✅ No fat interfaces                                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  D - Dependency Inversion Principle                             │
│  ────────────────────────────────────────────────────────────   │
│  ✅ RAGWorkflow depends on abstractions (interfaces)            │
│  ✅ Services injected via constructor                           │
│  ✅ No direct dependencies on concrete implementations          │
└─────────────────────────────────────────────────────────────────┘
```

## Component Interaction Example

```
User runs: python main.py

1. main.py loads configuration
   └─> config/settings.py reads .env

2. main.py initializes services
   ├─> GitHubRepositoryReader
   ├─> GoogleVisionAnalyzer ← NEW
   ├─> LocalFileReader ← NEW (uses GoogleVisionAnalyzer)
   ├─> DocumentChunker
   ├─> AzureOpenAIEmbeddingService
   └─> MilvusVectorStore

3. main.py creates RAGWorkflow
   └─> Injects all services (Dependency Injection)

4. main.py runs workflow
   └─> workflow.run(repo_url, data_dir, process_local=True)

5. Workflow executes steps:
   ├─> Step 1: Clone GitHub repository
   ├─> Step 2: Extract .md files
   ├─> Step 3: Process local files ← NEW
   │   ├─> Scan ./data/diagrams/
   │   ├─> For each image: GoogleVisionAnalyzer.analyze_image()
   │   ├─> For each .drawio: Read XML + analyze PNG export
   │   ├─> For each .docx: Extract paragraphs & tables
   │   └─> For each .xlsx: Extract sheet data
   ├─> Step 4: Chunk all documents
   ├─> Step 5: Create embeddings (Azure OpenAI)
   ├─> Step 6: Store in Milvus
   └─> Step 7: Cleanup

6. Result: All content searchable via vector similarity
```

## Configuration Flow

```
.env file
   │
   ├─> AZURE_OPENAI_API_KEY ──────────┐
   ├─> AZURE_OPENAI_ENDPOINT ─────────┤
   │                                   ▼
   ├─> MILVUS_URI ────────────┐  AzureOpenAIEmbeddingService
   ├─> MILVUS_TOKEN ──────────┤
   │                           ▼
   ├─> GITHUB_REPO_URL ─────  MilvusVectorStore
   │
   ├─> GOOGLE_APPLICATION_CREDENTIALS ─┐  ← NEW
   ├─> GOOGLE_VISION_MAX_RESULTS ──────┤
   │                                    ▼
   ├─> DATA_DIRECTORY ────────┐   GoogleVisionAnalyzer
   ├─> PROCESS_LOCAL_FILES ───┤
   │                           ▼
   ├─> CHUNK_SIZE ────────┐   LocalFileReader
   └─> CHUNK_OVERLAP ─────┘
                           │
                           ▼
                    DocumentChunker
```

## Summary

This architecture:
- ✅ Follows all SOLID principles
- ✅ Is fully extensible
- ✅ Has clear separation of concerns
- ✅ Supports dependency injection
- ✅ Handles multiple file types
- ✅ Integrates external APIs cleanly
- ✅ Maintains backward compatibility
- ✅ Is production-ready

All new components integrate seamlessly with existing architecture!

