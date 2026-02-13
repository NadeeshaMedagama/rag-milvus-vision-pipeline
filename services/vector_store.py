"""Milvus Cloud vector store implementation."""
import time
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
        # Validate input
        if not embedded_chunks:
            print("⚠️  No embedded chunks to insert, skipping...")
            return

        if not self.collection:
            self.collection = Collection(self.collection_name)

        # Get collection schema to determine field structure
        schema = self.collection.schema
        field_names = [field.name for field in schema.fields]

        print(f"Collection schema fields: {field_names}")
        print(f"Number of chunks to insert: {len(embedded_chunks)}")

        # Validate embedded chunks have required data
        for i, ec in enumerate(embedded_chunks):
            if ec.embedding is None:
                raise ValueError(f"Chunk {i} has no embedding")
            if ec.chunk is None:
                raise ValueError(f"Chunk {i} has no chunk data")

        # Prepare embeddings data
        embeddings = [ec.embedding for ec in embedded_chunks]

        # Prepare metadata fields (with safe defaults)
        contents = []
        file_paths = []
        repository_urls = []
        chunk_indices = []

        for ec in embedded_chunks:
            contents.append((ec.chunk.content or "")[:65535])  # Truncate if needed
            file_paths.append(ec.chunk.source_file_path or "")
            repository_urls.append(ec.chunk.repository_url or "")
            chunk_indices.append(ec.chunk.chunk_index if ec.chunk.chunk_index is not None else 0)

        # Build data list based on actual schema fields
        data = []

        # Check if this is old schema (2 fields) or new schema (6 fields)
        if len(field_names) == 2:
            print("⚠️  Warning: Collection has old schema (2 fields only)")
            print("⚠️  Metadata (content, file_path, etc.) will NOT be stored")
            print("⚠️  To use new schema with metadata, set FORCE_REPROCESS=true in .env")

            # For old schema, we need to match the field order and names exactly
            # Count non-auto-id fields to determine expected data lists
            non_auto_fields = [f for f in schema.fields if not (f.is_primary and f.auto_id)]
            print(f"Non-auto fields requiring data: {[f.name for f in non_auto_fields]}")

            for field in schema.fields:
                # Skip auto-generated primary key
                if field.is_primary and field.auto_id:
                    continue

                # Handle primary key without auto_id
                if field.is_primary and not field.auto_id:
                    # Generate sequential IDs starting from timestamp to avoid collisions
                    base_id = int(time.time() * 1000)
                    ids = [base_id + i for i in range(len(embedded_chunks))]
                    data.append(ids)
                elif field.dtype == DataType.FLOAT_VECTOR:
                    # This is the vector/embedding field
                    data.append(embeddings)
                elif field.dtype == DataType.VARCHAR:
                    # Unknown VARCHAR field - provide empty strings
                    print(f"⚠️  Unknown VARCHAR field in schema: {field.name}")
                    data.append(["" for _ in embedded_chunks])
                elif field.dtype == DataType.INT64:
                    # Unknown INT64 field - provide zeros
                    print(f"⚠️  Unknown INT64 field in schema: {field.name}")
                    data.append([0 for _ in embedded_chunks])
                else:
                    # Unknown field type - log warning but still try to provide data
                    print(f"⚠️  Unknown field type in schema: {field.name} (type: {field.dtype})")
                    # Try to provide default based on type
                    if "VARCHAR" in str(field.dtype):
                        data.append(["" for _ in embedded_chunks])
                    elif "INT" in str(field.dtype) or "FLOAT" in str(field.dtype):
                        data.append([0 for _ in embedded_chunks])
                    else:
                        print(f"❌ Cannot handle field type: {field.dtype}")
                        raise ValueError(f"Unsupported field type: {field.name} ({field.dtype})")
        else:
            # New schema: id, embedding, content, file_path, repository_url, chunk_index
            # Build data list based on actual schema fields (excluding auto_id primary key)
            for field in schema.fields:
                if field.is_primary and field.auto_id:
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
                elif field.dtype == DataType.FLOAT_VECTOR:
                    # Fallback for vector field with different name
                    data.append(embeddings)
                elif field.dtype == DataType.VARCHAR:
                    # Unknown VARCHAR field - provide empty strings
                    print(f"⚠️  Unknown VARCHAR field in schema: {field.name}")
                    data.append(["" for _ in embedded_chunks])
                elif field.dtype == DataType.INT64:
                    # Unknown INT64 field - provide zeros
                    print(f"⚠️  Unknown INT64 field in schema: {field.name}")
                    data.append([0 for _ in embedded_chunks])
                else:
                    # Handle any other fields with defaults
                    print(f"⚠️  Unhandled field in schema: {field.name} (type: {field.dtype})")
                    if "VARCHAR" in str(field.dtype):
                        data.append(["" for _ in embedded_chunks])
                    elif "INT" in str(field.dtype) or "FLOAT" in str(field.dtype):
                        data.append([0 for _ in embedded_chunks])
                    else:
                        print(f"❌ Cannot handle field type: {field.dtype}")
                        raise ValueError(f"Unsupported field type: {field.name} ({field.dtype})")

        # Validate data before insert
        if not data:
            raise ValueError("No data prepared for insertion - schema mismatch")

        expected_fields = len([f for f in schema.fields if not (f.is_primary and f.auto_id)])
        if len(data) != expected_fields:
            print(f"⚠️  Warning: Data list count ({len(data)}) doesn't match expected fields ({expected_fields})")
            print(f"   Schema fields: {field_names}")
            print(f"   Data lists prepared: {len(data)}")
            # Raise error instead of just warning - this will cause insert to fail
            raise ValueError(f"Data field count mismatch: got {len(data)}, expected {expected_fields}")

        # Validate all data lists have the same length
        for i, d in enumerate(data):
            if len(d) != len(embedded_chunks):
                raise ValueError(f"Data list {i} has {len(d)} items, expected {len(embedded_chunks)}")

        print(f"Inserting {len(embedded_chunks)} embeddings with {len(data)} data fields...")

        try:
            self.collection.insert(data)
            self.collection.flush()
            print(f"✅ Inserted {len(embedded_chunks)} embeddings into Milvus")
        except Exception as e:
            print(f"❌ Insert failed: {str(e)}")
            print(f"   Debug info:")
            print(f"   - Number of embedded chunks: {len(embedded_chunks)}")
            print(f"   - Number of data lists: {len(data)}")
            print(f"   - Length of each data list: {[len(d) for d in data]}")
            print(f"   - Schema fields (non-auto): {[f.name for f in schema.fields if not (f.is_primary and f.auto_id)]}")
            raise

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

