"""
Example script to test individual components.
Run this to verify your setup before running the full pipeline.
"""
import sys
from config import get_settings

def test_configuration():
    """Test if configuration loads correctly."""
    print("Testing configuration...")
    try:
        settings = get_settings()
        print("✓ Configuration loaded successfully")
        print(f"  - Azure OpenAI Endpoint: {settings.azure_openai_endpoint}")
        print(f"  - Milvus URI: {settings.milvus_uri}")
        print(f"  - GitHub Repo: {settings.github_repo_url}")
        print(f"  - Collection Name: {settings.milvus_collection_name}")
        return True
    except Exception as e:
        print(f"✗ Configuration failed: {str(e)}")
        return False


def test_azure_openai():
    """Test Azure OpenAI connection."""
    print("\nTesting Azure OpenAI connection...")
    try:
        from services import AzureOpenAIEmbeddingService
        settings = get_settings()

        service = AzureOpenAIEmbeddingService(
            api_key=settings.azure_openai_api_key,
            endpoint=settings.azure_openai_endpoint,
            deployment_name=settings.azure_openai_embedding_deployment,
            api_version=settings.azure_openai_api_version
        )

        # Test with a simple text
        test_text = "This is a test"
        embedding = service.create_embedding(test_text)

        print(f"✓ Azure OpenAI connection successful")
        print(f"  - Embedding dimension: {len(embedding)}")
        return True
    except Exception as e:
        print(f"✗ Azure OpenAI connection failed: {str(e)}")
        return False


def test_milvus():
    """Test Milvus Cloud connection."""
    print("\nTesting Milvus Cloud connection...")
    try:
        from services import MilvusVectorStore
        settings = get_settings()

        vector_store = MilvusVectorStore(
            uri=settings.milvus_uri,
            token=settings.milvus_token,
            collection_name=f"test_collection_{settings.milvus_collection_name}",
            embedding_dimension=settings.embedding_dimension
        )

        print("✓ Milvus Cloud connection successful")

        # Clean up test collection
        try:
            vector_store.delete_collection()
            print("  - Test collection cleaned up")
        except:
            pass

        return True
    except Exception as e:
        print(f"✗ Milvus Cloud connection failed: {str(e)}")
        return False


def test_github():
    """Test GitHub repository access."""
    print("\nTesting GitHub repository access...")
    try:
        from services import GitHubRepositoryReader
        settings = get_settings()

        # Note: This doesn't actually clone, just validates the URL format
        reader = GitHubRepositoryReader(github_token=settings.github_token)

        # Check if URL is valid
        if settings.github_repo_url.startswith("https://github.com/"):
            print("✓ GitHub repository URL format is valid")
            print(f"  - Repository: {settings.github_repo_url}")
            return True
        else:
            print("✗ Invalid GitHub repository URL format")
            return False
    except Exception as e:
        print(f"✗ GitHub setup failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("RAG Application Setup Test")
    print("="*60)

    results = {
        "Configuration": test_configuration(),
        "Azure OpenAI": test_azure_openai(),
        "Milvus Cloud": test_milvus(),
        "GitHub": test_github()
    }

    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)

    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:20s}: {status}")
        if not passed:
            all_passed = False

    print("="*60)

    if all_passed:
        print("\n✅ All tests passed! You're ready to run the RAG pipeline.")
        print("\nNext steps:")
        print("  1. Run: python main.py (to index documents)")
        print("  2. Run: python query.py (to search documents)")
        return 0
    else:
        print("\n❌ Some tests failed. Please check your .env configuration.")
        print("\nCommon issues:")
        print("  - Check Azure OpenAI API key and endpoint")
        print("  - Verify Milvus Cloud URI and token")
        print("  - Ensure GitHub repository URL is correct")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

