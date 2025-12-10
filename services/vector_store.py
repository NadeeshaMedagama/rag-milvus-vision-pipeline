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

        # Get collection schema to determine field structure
        schema = self.collection.schema
        field_names = [field.name for field in schema.fields]

        print(f"Collection schema fields: {field_names}")

        # Prepare embeddings data
        embeddings = [ec.embedding for ec in embedded_chunks]

        # Build data list based on actual schema fields
        data = []

        # Check if this is old schema (2 fields) or new schema (6 fields)
        if len(field_names) == 2:
            print("⚠️  Warning: Collection has old schema (2 fields only)")
            print("⚠️  Metadata (content, file_path, etc.) will NOT be stored")
            print("⚠️  To use new schema with metadata, set FORCE_REPROCESS=true in .env")

            # For old schema, we need to match the field order and names exactly
            for field in schema.fields:
                if field.name == "id":
                    if field.auto_id:
                        continue  # Skip auto-generated ID
                    else:
                        # If ID is not auto-generated, we need to provide IDs
                        # This shouldn't happen in modern Milvus, but handle it
                        ids = list(range(len(embedded_chunks)))
                        data.append(ids)
                elif field.name == "vector" or field.name == "embedding":
                    # Old schema might use 'vector' instead of 'embedding'
                    data.append(embeddings)
        else:
            # New schema: id, embedding, content, file_path, repository_url, chunk_index
            contents = [ec.chunk.content[:65535] for ec in embedded_chunks]  # Truncate if needed
            file_paths = [ec.chunk.source_file_path for ec in embedded_chunks]
            repository_urls = [ec.chunk.repository_url for ec in embedded_chunks]
            chunk_indices = [ec.chunk.chunk_index for ec in embedded_chunks]

            # Build data list based on actual schema fields (excluding auto_id primary key)
            for field in schema.fields:
                if field.name == "id" and field.auto_id:
                    continue  # Skip auto-generated ID field
                elif field.name == "embedding" or field.name == "vector":
                    data.append(embeddings)
                elif field.name == "content":
                    data.append(contents)
                elif field.name == "file_path":
                    data.append(file_paths)
                elif field.name == "repository_url":
                    data.append(repository_urls)
                elif field.name == "chunk_index":
                    data.append(chunk_indices)

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

        # Determine the vector field name (could be 'embedding' or 'vector')
        schema = self.collection.schema
        field_names = [field.name for field in schema.fields]

        vector_field = "embedding" if "embedding" in field_names else "vector"

        # Determine which output fields are available
        available_output_fields = []
        for field_name in ["content", "file_path", "repository_url", "chunk_index"]:
            if field_name in field_names:
                available_output_fields.append(field_name)

        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10}
        }

        results = self.collection.search(
            data=[query_embedding],
            anns_field=vector_field,
            param=search_params,
            limit=top_k,
            output_fields=available_output_fields if available_output_fields else None
        )

        # Format results
        formatted_results = []
        for hits in results:
            for hit in hits:
                result = {
                    "id": hit.id,
                    "distance": hit.distance,
                }

                # Add metadata fields if available
                if available_output_fields:
                    result["content"] = hit.entity.get("content")
                    result["file_path"] = hit.entity.get("file_path")
                    result["repository_url"] = hit.entity.get("repository_url")
                    result["chunk_index"] = hit.entity.get("chunk_index")
                else:
                    result["content"] = None
                    result["file_path"] = None
                    result["repository_url"] = None
                    result["chunk_index"] = None

                formatted_results.append(result)

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

            # Show schema information
            schema = self.collection.schema
            field_names = [field.name for field in schema.fields]
            print(f"Collection schema: {', '.join(field_names)}")

            # Check if schema matches expected structure
            expected_fields = ["id", "embedding", "content", "file_path", "repository_url", "chunk_index"]
            if len(field_names) < len(expected_fields):
                print("\n" + "="*60)
                print("⚠️  SCHEMA COMPATIBILITY MODE")
                print("="*60)
                print(f"Existing collection has {len(field_names)} fields: {', '.join(field_names)}")
                print(f"New schema expects {len(expected_fields)} fields: {', '.join(expected_fields)}")
                print("\nThe system will work in COMPATIBILITY MODE:")
                print("✓ New data will be inserted using existing schema")
                print("✓ Existing data will NOT be deleted")
                print("⚠️  Some metadata may not be stored")
                print("\n💡 To use full schema with metadata:")
                print("   1. Set FORCE_REPROCESS=true in .env")
                print("   2. Run the pipeline again")
                print("   (This will recreate the collection with new schema)")
                print("="*60 + "\n")
        else:
            print(f"Collection '{self.collection_name}' does not exist. Creating new collection...")
            self.initialize_collection()

