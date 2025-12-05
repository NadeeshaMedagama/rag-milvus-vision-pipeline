#!/bin/bash

# Installation script for Python RAG with Milvus and Google Vision API
# This script installs all required dependencies

echo "=================================="
echo "Python RAG with Milvus Installer"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if Python 3.8 or higher
required_version="3.8"
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "Error: Python 3.8 or higher is required"
    exit 1
fi

echo "✓ Python version is compatible"
echo ""

# Install requirements
echo "Installing Python packages..."
echo "This may take a few minutes..."
echo ""

pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✓ Installation completed successfully!"
    echo "=================================="
    echo ""
    echo "Next steps:"
    echo "1. Copy .env.example to .env:"
    echo "   cp .env.example .env"
    echo ""
    echo "2. Edit .env and add your credentials:"
    echo "   - Azure OpenAI API credentials"
    echo "   - Milvus Cloud credentials"
    echo "   - GitHub repository URL"
    echo "   - Google Vision API credentials (in ./credentials/ folder)"
    echo ""
    echo "3. Test your setup:"
    echo "   python test_setup.py"
    echo ""
    echo "4. Run the application:"
    echo "   python main.py"
    echo ""
    echo "For detailed setup instructions, see docs/GOOGLE_VISION_SETUP.md"
else
    echo ""
    echo "=================================="
    echo "✗ Installation failed!"
    echo "=================================="
    echo ""
    echo "Please check the error messages above and try again."
    exit 1
fi

