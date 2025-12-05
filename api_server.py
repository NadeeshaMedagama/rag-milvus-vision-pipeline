"""Simple REST API for testing Milvus data retrieval."""
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import get_settings
from services import AzureOpenAIEmbeddingService, MilvusVectorStore
from query import RAGQueryService

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize services
settings = get_settings()

embedding_service = AzureOpenAIEmbeddingService(
    api_key=settings.azure_openai_api_key,
    endpoint=settings.azure_openai_endpoint,
    deployment_name=settings.azure_openai_embedding_deployment,
    api_version=settings.azure_openai_api_version
)

vector_store = MilvusVectorStore(
    uri=settings.milvus_uri,
    token=settings.milvus_token,
    collection_name=settings.milvus_collection_name,
    embedding_dimension=settings.embedding_dimension
)

query_service = RAGQueryService(
    embedding_service=embedding_service,
    vector_store=vector_store
)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'RAG Query API',
        'version': '1.0.0'
    })


@app.route('/api/query', methods=['POST'])
def query():
    """
    Query the RAG system.
    
    Expected JSON body:
    {
        "query": "your query text",
        "top_k": 5  # optional, default is 5
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Missing required field: query',
                'example': {
                    'query': 'What is the architecture?',
                    'top_k': 5
                }
            }), 400
        
        query_text = data['query']
        top_k = data.get('top_k', 5)
        
        # Validate top_k
        if not isinstance(top_k, int) or top_k < 1 or top_k > 100:
            return jsonify({
                'error': 'top_k must be an integer between 1 and 100'
            }), 400
        
        # Perform search
        results = query_service.query(query_text, top_k=top_k)
        
        return jsonify({
            'success': True,
            'query': query_text,
            'results_count': len(results),
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def stats():
    """Get collection statistics."""
    try:
        collection_exists = vector_store.collection_exists()
        
        if not collection_exists:
            return jsonify({
                'success': True,
                'collection_exists': False,
                'message': f'Collection "{settings.milvus_collection_name}" does not exist'
            })
        
        # Get collection info
        collection = vector_store.collection
        if not collection:
            from pymilvus import Collection
            collection = Collection(settings.milvus_collection_name)
        
        collection.load()
        num_entities = collection.num_entities
        
        return jsonify({
            'success': True,
            'collection_exists': True,
            'collection_name': settings.milvus_collection_name,
            'total_documents': num_entities,
            'embedding_dimension': settings.embedding_dimension
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/test-retrieval', methods=['GET'])
def test_retrieval():
    """
    Simple test endpoint to verify data retrieval is working.
    Uses a generic query to fetch some results.
    """
    try:
        # Check if collection exists
        if not vector_store.collection_exists():
            return jsonify({
                'success': False,
                'error': f'Collection "{settings.milvus_collection_name}" does not exist',
                'message': 'Please run main.py first to create and populate the collection'
            }), 404
        
        # Use a generic query
        test_query = "architecture"
        results = query_service.query(test_query, top_k=3)
        
        if not results:
            return jsonify({
                'success': True,
                'message': 'Collection exists but no results found for test query',
                'test_query': test_query,
                'results_count': 0
            })
        
        return jsonify({
            'success': True,
            'message': 'Data retrieval is working!',
            'test_query': test_query,
            'results_count': len(results),
            'sample_results': [
                {
                    'file_path': r['file_path'],
                    'distance': r['distance'],
                    'content_preview': r['content'][:150] + '...' if len(r['content']) > 150 else r['content']
                }
                for r in results
            ]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/', methods=['GET'])
def index():
    """API documentation."""
    return jsonify({
        'service': 'RAG Query API',
        'version': '1.0.0',
        'endpoints': {
            'GET /health': 'Health check',
            'GET /': 'API documentation (this page)',
            'GET /api/test-retrieval': 'Test data retrieval from Milvus',
            'GET /api/stats': 'Get collection statistics',
            'POST /api/query': 'Query the RAG system',
        },
        'examples': {
            'test_retrieval': 'curl http://localhost:5000/api/test-retrieval',
            'stats': 'curl http://localhost:5000/api/stats',
            'query': 'curl -X POST http://localhost:5000/api/query -H "Content-Type: application/json" -d \'{"query": "What is the architecture?", "top_k": 5}\''
        }
    })


if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 Starting RAG Query API Server")
    print("="*80)
    print(f"Collection: {settings.milvus_collection_name}")
    print(f"Milvus URI: {settings.milvus_uri}")
    print("\nAvailable endpoints:")
    print("  GET  http://localhost:5000/              - API documentation")
    print("  GET  http://localhost:5000/health        - Health check")
    print("  GET  http://localhost:5000/api/test-retrieval - Test data retrieval")
    print("  GET  http://localhost:5000/api/stats     - Collection statistics")
    print("  POST http://localhost:5000/api/query     - Query the RAG system")
    print("\n" + "="*80)
    print("Press CTRL+C to stop the server")
    print("="*80 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

