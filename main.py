"""Main application entry point for the RAG system."""
from config import get_settings
from services import (
    GitHubRepositoryReader,
    DocumentChunker,
    AzureOpenAIEmbeddingService,
    MilvusVectorStore,
    GoogleVisionAnalyzer,
    LocalFileReader
)
from workflows import RAGWorkflow


def main():
    """Main function to run the RAG application."""
    # Load settings from .env file
    print("Loading configuration...")
    settings = get_settings()

    # Initialize services (Dependency Injection - following SOLID principles)
    print("Initializing services...")

    # Repository reader service
    repository_reader = GitHubRepositoryReader(
        github_token=settings.github_token
    )

    # Document chunker service
    document_chunker = DocumentChunker(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )

    # Embedding service
    embedding_service = AzureOpenAIEmbeddingService(
        api_key=settings.azure_openai_api_key,
        endpoint=settings.azure_openai_endpoint,
        deployment_name=settings.azure_openai_embedding_deployment,
        api_version=settings.azure_openai_api_version
    )

    # Vector store service
    vector_store = MilvusVectorStore(
        uri=settings.milvus_uri,
        token=settings.milvus_token,
        collection_name=settings.milvus_collection_name,
        embedding_dimension=settings.embedding_dimension
    )

    # Google Vision API service (for analyzing diagrams and images)
    vision_analyzer = None
    local_file_reader = None

    if settings.process_local_files:
        try:
            print("Initializing Google Vision API service...")
            vision_analyzer = GoogleVisionAnalyzer(
                credentials_path=settings.google_application_credentials,
                max_results=settings.google_vision_max_results
            )

            # Local file reader service (uses Vision API for images)
            local_file_reader = LocalFileReader(
                vision_analyzer=vision_analyzer
            )
            print("✓ Google Vision API and Local File Reader initialized")
        except Exception as e:
            print(f"Warning: Failed to initialize Google Vision API: {str(e)}")
            print("Continuing without local file processing...")

    # Create workflow
    print("Creating RAG workflow...")
    workflow = RAGWorkflow(
        repository_reader=repository_reader,
        document_chunker=document_chunker,
        embedding_service=embedding_service,
        vector_store=vector_store,
        local_file_reader=local_file_reader
    )

    # Run workflow
    final_state = workflow.run(
        repository_url=settings.github_repo_url,
        local_data_dir=settings.data_directory,
        process_local_files=settings.process_local_files,
        skip_existing_documents=settings.skip_existing_documents,
        force_reprocess=settings.force_reprocess
    )

    # Display results
    if final_state["status"] == "completed":
        print("\n✅ RAG pipeline completed successfully!")
        print(f"\nYou can now query the vector store using the search functionality.")
        print(f"Collection name: {settings.milvus_collection_name}")
    elif final_state["status"] == "completed_no_changes":
        print("\n✅ All documents already indexed!")
        print(f"\nYou can query the vector store using the search functionality.")
        print(f"Collection name: {settings.milvus_collection_name}")
        print(f"\n💡 To force reprocessing, set FORCE_REPROCESS=true in .env")
    else:
        print("\n❌ RAG pipeline failed!")
        if final_state.get("error"):
            print(f"Error: {final_state['error']}")
        return 1

    return 0


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

