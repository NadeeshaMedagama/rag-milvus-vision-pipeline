"""Query interface for searching the RAG system."""
from typing import List, Dict
from config import get_settings
from services import AzureOpenAIEmbeddingService, MilvusVectorStore


class RAGQueryService:
    """Service for querying the RAG system."""

    def __init__(
        self,
        embedding_service: AzureOpenAIEmbeddingService,
        vector_store: MilvusVectorStore
    ):
        """
        Initialize the query service.

        Args:
            embedding_service: Service for creating embeddings
            vector_store: Vector store for searching
        """
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def query(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """
        Query the RAG system.

        Args:
            query_text: Query text
            top_k: Number of results to return

        Returns:
            List of search results
        """
        # Create embedding for query
        print(f"Creating embedding for query: {query_text}")
        query_embedding = self.embedding_service.create_embedding(query_text)

        # Search in vector store
        print(f"Searching for top {top_k} results...")
        results = self.vector_store.search(query_embedding, top_k=top_k)

        return results

    def display_results(self, results: List[Dict]) -> None:
        """
        Display search results in a readable format.

        Args:
            results: Search results to display
        """
        print(f"\n{'='*80}")
        print(f"Found {len(results)} results:")
        print(f"{'='*80}\n")

        for idx, result in enumerate(results, 1):
            print(f"Result #{idx}")
            print(f"  File: {result['file_path']}")
            print(f"  Chunk Index: {result['chunk_index']}")
            print(f"  Distance: {result['distance']:.4f}")
            print(f"  Content Preview:")
            content_preview = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
            print(f"    {content_preview}")
            print(f"{'-'*80}\n")


def main():
    """Main function for querying the RAG system."""
    # Load settings
    settings = get_settings()

    # Initialize services
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

    # Create query service
    query_service = RAGQueryService(
        embedding_service=embedding_service,
        vector_store=vector_store
    )

    # Interactive query loop
    print("\n" + "="*80)
    print("RAG Query System - Interactive Mode")
    print("="*80)
    print("Enter your queries (type 'exit' or 'quit' to stop)")
    print("="*80 + "\n")

    while True:
        try:
            query = input("\nEnter your query: ").strip()

            if query.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break

            if not query:
                print("Please enter a query.")
                continue

            # Perform search
            results = query_service.query(query, top_k=5)
            query_service.display_results(results)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()

