#!/bin/bash

# Simple curl command reference for testing Milvus retrieval

echo "======================================================================"
echo "🔍 CURL COMMANDS FOR TESTING MILVUS DATA RETRIEVAL"
echo "======================================================================"
echo ""
echo "Prerequisites:"
echo "  1. Run: python main.py (to populate Milvus)"
echo "  2. Run: python api_server.py (in another terminal)"
echo ""
echo "======================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Health Check${NC}"
echo "curl http://localhost:5000/health"
echo ""

echo -e "${BLUE}2. API Documentation${NC}"
echo "curl http://localhost:5000/"
echo ""

echo -e "${YELLOW}3. ⭐ TEST DATA RETRIEVAL (MAIN TEST)${NC}"
echo "curl http://localhost:5000/api/test-retrieval"
echo ""

echo -e "${BLUE}4. Collection Statistics${NC}"
echo "curl http://localhost:5000/api/stats"
echo ""

echo -e "${BLUE}5. Query Your Data${NC}"
echo "curl -X POST http://localhost:5000/api/query \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"query\": \"architecture\"}'"
echo ""

echo -e "${BLUE}6. Query with Custom top_k${NC}"
echo "curl -X POST http://localhost:5000/api/query \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"query\": \"Choreo architecture\", \"top_k\": 10}'"
echo ""

echo -e "${BLUE}7. Pretty Print with jq (if installed)${NC}"
echo "curl -s http://localhost:5000/api/test-retrieval | jq"
echo ""

echo "======================================================================"
echo -e "${GREEN}✅ ONE-LINER TEST COMMAND:${NC}"
echo "======================================================================"
echo "curl -s http://localhost:5000/api/test-retrieval | python -m json.tool"
echo ""
echo "Or with jq (prettier):"
echo "curl -s http://localhost:5000/api/test-retrieval | jq"
echo ""
echo "======================================================================"

