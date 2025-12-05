"""Milvus Cloud vector store implementation."""
from typing import List
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)

from interfaces import IVectorStore
from models import EmbeddedChunk


class MilvusVectorStore(IVectorStore):
    """Service for managing embeddings in Milvus Cloud."""

    def __init__(
        self,
        uri: str,
        token: str,
        collection_name: str,
        embedding_dimension: int = 1536
    ):
        """
        Initialize the Milvus vector store.

        Args:
            uri: Milvus Cloud URI
            token: Milvus Cloud token
            collection_name: Name of the collection
            embedding_dimension: Dimension of the embeddings
        """
        self.uri = uri
        self.token = token
        self.collection_name = collection_name
        self.embedding_dimension = embedding_dimension
        self.collection = None

        # Connect to Milvus Cloud
        self._connect()

    def _connect(self) -> None:
        """Connect to Milvus Cloud."""
        connections.connect(
            alias="default",
            uri=self.uri,
            token=self.token
        )
        print("Connected to Milvus Cloud")

    def initialize_collection(self) -> None:
        """Initialize the vector collection."""
        # Drop existing collection if it exists
        if utility.has_collection(self.collection_name):
            print(f"Dropping existing collection: {self.collection_name}")
            utility.drop_collection(self.collection_name)

        # Define schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dimension),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="file_path", dtype=DataType.VARCHAR, max_length=1000),
            FieldSchema(name="repository_url", dtype=DataType.VARCHAR, max_length=1000),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
        ]

        schema = CollectionSchema(
            fields=fields,
            description="RAG embeddings for markdown files"
        )

        # Create collection
        self.collection = Collection(
            name=self.collection_name,
            schema=schema
        )

        # Create index for vector field
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }

        self.collection.create_index(
            field_name="embedding",
            index_params=index_params
        )

        print(f"Created collection: {self.collection_name}")

    def insert_embeddings(self, embedded_chunks: List[EmbeddedChunk]) -> None:
        """
        Insert embeddings into the vector store.

        Args:
            embedded_chunks: List of embedded chunks to insert
        """
        if not self.collection:
            self.collection = Collection(self.collection_name)

        # Prepare data for insertion
        embeddings = [ec.embedding for ec in embedded_chunks]
        contents = [ec.chunk.content[:65535] for ec in embedded_chunks]  # Truncate if needed
        file_paths = [ec.chunk.source_file_path for ec in embedded_chunks]
        repository_urls = [ec.chunk.repository_url for ec in embedded_chunks]
        chunk_indices = [ec.chunk.chunk_index for ec in embedded_chunks]

        # Insert data
        data = [
            embeddings,
            contents,
            file_paths,
            repository_urls,
            chunk_indices
        ]

        self.collection.insert(data)
        self.collection.flush()
        print(f"Inserted {len(embedded_chunks)} embeddings into Milvus")

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[dict]:
        """
        Search for similar embeddings.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return

        Returns:
            List of search results
        """
        if not self.collection:
            self.collection = Collection(self.collection_name)

        self.collection.load()

        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10}
        }

        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["content", "file_path", "repository_url", "chunk_index"]
        )

        # Format results
        formatted_results = []
        for hits in results:
            for hit in hits:
                formatted_results.append({
                    "id": hit.id,
                    "distance": hit.distance,
                    "content": hit.entity.get("content"),
                    "file_path": hit.entity.get("file_path"),
                    "repository_url": hit.entity.get("repository_url"),
                    "chunk_index": hit.entity.get("chunk_index")
                })

        return formatted_results

    def delete_collection(self) -> None:
        """Delete the collection."""
        if utility.has_collection(self.collection_name):
            utility.drop_collection(self.collection_name)
            print(f"Deleted collection: {self.collection_name}")

    def collection_exists(self) -> bool:
        """
        Check if collection exists.

        Returns:
            True if collection exists, False otherwise
        """
        return utility.has_collection(self.collection_name)

    def get_existing_file_paths(self) -> set:
        """
        Get set of file paths that already exist in the collection.

        Returns:
            Set of file paths already indexed
        """
        if not self.collection_exists():
            return set()

        if not self.collection:
            self.collection = Collection(self.collection_name)

        self.collection.load()

        # Query to get all unique file paths
        try:
            # Get all entities
            query_result = self.collection.query(
                expr="id > 0",
                output_fields=["file_path"],
                limit=16384  # Milvus limit
            )

            file_paths = set([item.get("file_path") for item in query_result if item.get("file_path")])
            return file_paths
        except Exception as e:
            print(f"Warning: Could not retrieve existing file paths: {str(e)}")
            return set()

    def get_document_count(self) -> int:
        """
        Get total number of documents in collection.

        Returns:
            Number of documents
        """
        if not self.collection_exists():
            return 0

        if not self.collection:
            self.collection = Collection(self.collection_name)

        return self.collection.num_entities

    def initialize_or_load_collection(self) -> None:
        """Initialize collection if it doesn't exist, or load existing one."""
        if self.collection_exists():
            print(f"Collection '{self.collection_name}' already exists. Loading...")
            self.collection = Collection(self.collection_name)
            existing_count = self.get_document_count()
            print(f"Found {existing_count} existing documents in collection")
        else:
            print(f"Collection '{self.collection_name}' does not exist. Creating new collection...")
            self.initialize_collection()

