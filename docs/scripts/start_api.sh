#!/bin/bash

# Quick Start Script for Testing Milvus Retrieval

echo "=================================="
echo "🔍 Milvus Retrieval Test Script"
echo "=================================="
echo ""

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing Flask dependencies..."
    pip install flask flask-cors
    echo ""
fi

# Check if collection exists
echo "🔍 Checking if Milvus collection exists..."
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
    print('✅ Collection \"{}\" exists!'.format(settings.milvus_collection_name))
    collection = vs.collection
    if not collection:
        from pymilvus import Collection
        collection = Collection(settings.milvus_collection_name)
    collection.load()
    print('📊 Total documents:', collection.num_entities)
else:
    print('❌ Collection does not exist.')
    print('📝 Run \"python main.py\" first to create and populate the collection.')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo ""
    echo "=================================="
    echo "⚠️  Please run the pipeline first:"
    echo "    python main.py"
    echo "=================================="
    exit 1
fi

echo ""
echo "=================================="
echo "🚀 Starting API Server..."
echo "=================================="
echo ""
echo "The server will start on http://localhost:5000"
echo ""
echo "📝 In another terminal, run these commands:"
echo ""
echo "# Test data retrieval"
echo "curl http://localhost:5000/api/test-retrieval"
echo ""
echo "# Query your data"
echo "curl -X POST http://localhost:5000/api/query \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"query\": \"architecture\"}'"
echo ""
echo "=================================="
echo "Press CTRL+C to stop the server"
echo "=================================="
echo ""

# Start the API server
python api_server.py

