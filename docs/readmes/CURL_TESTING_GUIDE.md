# 🔍 Testing Milvus Data Retrieval with curl

This guide shows you how to test data retrieval from your Milvus vector database using simple curl commands.

---

## 🚀 Quick Start

### Step 1: Install Flask Dependencies

```bash
pip install flask flask-cors
```

### Step 2: Start the API Server

```bash
python api_server.py
```

You should see:
```
================================================================================
🚀 Starting RAG Query API Server
================================================================================
Collection: readme_embeddings
Milvus URI: https://your-instance.zillizcloud.com:19530

Available endpoints:
  GET  http://localhost:5000/              - API documentation
  GET  http://localhost:5000/health        - Health check
  GET  http://localhost:5000/api/test-retrieval - Test data retrieval
  GET  http://localhost:5000/api/stats     - Collection statistics
  POST http://localhost:5000/api/query     - Query the RAG system

================================================================================
Press CTRL+C to stop the server
================================================================================
```

### Step 3: Open a New Terminal and Test with curl

---

## 📝 curl Commands

### 1. Health Check (Verify API is Running)

```bash
curl http://localhost:5000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "RAG Query API",
  "version": "1.0.0"
}
```

---

### 2. API Documentation

```bash
curl http://localhost:5000/
```

**Expected Response:**
```json
{
  "service": "RAG Query API",
  "version": "1.0.0",
  "endpoints": {
    "GET /health": "Health check",
    "GET /": "API documentation (this page)",
    "GET /api/test-retrieval": "Test data retrieval from Milvus",
    "GET /api/stats": "Get collection statistics",
    "POST /api/query": "Query the RAG system"
  },
  "examples": {
    "test_retrieval": "curl http://localhost:5000/api/test-retrieval",
    "stats": "curl http://localhost:5000/api/stats",
    "query": "curl -X POST http://localhost:5000/api/query -H \"Content-Type: application/json\" -d '{\"query\": \"What is the architecture?\", \"top_k\": 5}'"
  }
}
```

---

### 3. Test Data Retrieval (⭐ MAIN TEST)

```bash
curl http://localhost:5000/api/test-retrieval
```

**Expected Response (Success):**
```json
{
  "success": true,
  "message": "Data retrieval is working!",
  "test_query": "architecture",
  "results_count": 3,
  "sample_results": [
    {
      "file_path": "README.md",
      "distance": 0.1234,
      "content_preview": "# Architecture Documentation\nThis document describes the system architecture..."
    },
    {
      "file_path": "data/diagrams/architecture.drawio.png",
      "distance": 0.2345,
      "content_preview": "File: architecture.drawio.png\nLabels detected: Architecture, Diagram, Cloud..."
    },
    {
      "file_path": "docs/ARCHITECTURE.md",
      "distance": 0.3456,
      "content_preview": "## System Architecture\nThe system consists of multiple components..."
    }
  ]
}
```

**Expected Response (No Data Yet):**
```json
{
  "success": false,
  "error": "Collection \"readme_embeddings\" does not exist",
  "message": "Please run main.py first to create and populate the collection"
}
```

---

### 4. Collection Statistics

```bash
curl http://localhost:5000/api/stats
```

**Expected Response (With Data):**
```json
{
  "success": true,
  "collection_exists": true,
  "collection_name": "readme_embeddings",
  "total_documents": 150,
  "embedding_dimension": 1536
}
```

**Expected Response (No Data):**
```json
{
  "success": true,
  "collection_exists": false,
  "message": "Collection \"readme_embeddings\" does not exist"
}
```

---

### 5. Query the RAG System

#### Basic Query
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the architecture?"}'
```

#### Query with Custom top_k
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain the Choreo control plane", "top_k": 10}'
```

#### Pretty Print Response (with jq)
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the architecture?"}' | jq
```

**Expected Response:**
```json
{
  "success": true,
  "query": "What is the architecture?",
  "results_count": 5,
  "results": [
    {
      "id": 442893740857426944,
      "distance": 0.1234,
      "content": "# Architecture Documentation\n\nThis document describes...",
      "file_path": "README.md",
      "repository_url": "https://github.com/...",
      "chunk_index": 0
    },
    {
      "id": 442893740857426945,
      "distance": 0.2345,
      "content": "The control plane consists of...",
      "file_path": "docs/ARCHITECTURE.md",
      "repository_url": "https://github.com/...",
      "chunk_index": 2
    }
  ]
}
```

---

## 🎯 Complete Testing Workflow

### 1️⃣ First, Make Sure You Have Data

```bash
# Run the main pipeline to populate Milvus
python main.py
```

Wait for completion:
```
✅ RAG pipeline completed successfully!
```

### 2️⃣ Start the API Server

```bash
# In one terminal
python api_server.py
```

### 3️⃣ Test Retrieval in Another Terminal

```bash
# 1. Check API health
curl http://localhost:5000/health

# 2. Check collection stats
curl http://localhost:5000/api/stats

# 3. Test data retrieval (MAIN TEST)
curl http://localhost:5000/api/test-retrieval

# 4. Try a custom query
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "architecture diagram"}'
```

---

## 📊 Understanding the Response

### Success Indicators

✅ **Collection Exists:**
```json
{
  "collection_exists": true,
  "total_documents": 150
}
```

✅ **Data Retrieval Working:**
```json
{
  "success": true,
  "message": "Data retrieval is working!",
  "results_count": 3
}
```

✅ **Query Results:**
```json
{
  "success": true,
  "results_count": 5,
  "results": [...]
}
```

### Error Indicators

❌ **Collection Doesn't Exist:**
```json
{
  "success": false,
  "error": "Collection \"readme_embeddings\" does not exist"
}
```
**Solution:** Run `python main.py` first

❌ **No Results Found:**
```json
{
  "success": true,
  "results_count": 0
}
```
**Reason:** Collection is empty or query doesn't match any documents

---

## 🔧 Advanced curl Examples

### Save Response to File
```bash
curl http://localhost:5000/api/test-retrieval > response.json
```

### Pretty Print with jq
```bash
curl http://localhost:5000/api/stats | jq '.'
```

### Show Only Success Status
```bash
curl -s http://localhost:5000/api/test-retrieval | jq '.success'
```

### Show Only Result Count
```bash
curl -s http://localhost:5000/api/test-retrieval | jq '.results_count'
```

### Extract File Paths from Results
```bash
curl -s -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "architecture"}' | jq '.results[].file_path'
```

### Multiple Queries in Sequence
```bash
for query in "architecture" "diagram" "API" "database"; do
  echo "Query: $query"
  curl -s -X POST http://localhost:5000/api/query \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$query\", \"top_k\": 3}" | jq '.results_count'
  echo ""
done
```

---

## 🐛 Troubleshooting

### Issue: Connection Refused

**Error:**
```
curl: (7) Failed to connect to localhost port 5000: Connection refused
```

**Solution:**
- Make sure `python api_server.py` is running
- Check if another application is using port 5000

### Issue: ModuleNotFoundError: No module named 'flask'

**Solution:**
```bash
pip install flask flask-cors
```

### Issue: Collection doesn't exist

**Solution:**
```bash
# Run the main pipeline first
python main.py
```

### Issue: Empty Results

**Check:**
```bash
# Verify collection has data
curl http://localhost:5000/api/stats

# Should show: "total_documents": > 0
```

---

## 📱 Testing from Other Machines

### If testing from the same machine:
```bash
curl http://localhost:5000/api/test-retrieval
```

### If testing from another machine on the same network:
```bash
# Replace YOUR_IP with your machine's IP address
curl http://YOUR_IP:5000/api/test-retrieval
```

### Find your IP address:
```bash
# Linux/Mac
ip addr show | grep "inet " | grep -v 127.0.0.1

# Or
hostname -I
```

---

## 🎯 One-Liner Test Command

**Single command to verify everything is working:**

```bash
curl -s http://localhost:5000/api/test-retrieval | jq -r 'if .success then "✅ SUCCESS: Milvus retrieval is working! Found \(.results_count) results." else "❌ ERROR: \(.error // .message)" end'
```

**Expected Output:**
```
✅ SUCCESS: Milvus retrieval is working! Found 3 results.
```

---

## 📝 Alternative: Direct Python Test (No API Server)

If you prefer not to use the API server, you can test directly with Python:

```bash
python -c "
from config import get_settings
from services import MilvusVectorStore

settings = get_settings()
vs = MilvusVectorStore(
    uri=settings.milvus_uri,
    token=settings.milvus_token,
    collection_name=settings.milvus_collection_name,
    embedding_dimension=settings.embedding_dimension
)

if vs.collection_exists():
    print('✅ Collection exists!')
    print(f'Collection name: {settings.milvus_collection_name}')
else:
    print('❌ Collection does not exist. Run main.py first.')
"
```

---

## 🎊 Summary

### ✅ Main Test Command (Use This First!)

```bash
curl http://localhost:5000/api/test-retrieval
```

### ✅ Query Your Own Data

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "YOUR_QUERY_HERE"}'
```

### ✅ Check Collection Stats

```bash
curl http://localhost:5000/api/stats
```

---

**That's it! You now have a simple REST API to test your Milvus data retrieval with curl commands! 🚀**

