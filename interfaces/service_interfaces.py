"""Abstract interfaces for the RAG application (Interface Segregation Principle)."""
from abc import ABC, abstractmethod
from typing import List
from models.data_models import Document, Chunk, EmbeddedChunk


class IRepositoryReader(ABC):
    """Interface for reading documents from a repository."""

    @abstractmethod
    def clone_repository(self, repo_url: str) -> str:
        """Clone a repository and return the local path."""
        pass

    @abstractmethod
    def get_markdown_files(self, repo_path: str) -> List[Document]:
        """Get all markdown files from the repository."""
        pass

    @abstractmethod
    def cleanup(self, repo_path: str) -> None:
        """Clean up the cloned repository."""
        pass


class ILocalFileReader(ABC):
    """Interface for reading local files and directories."""

    @abstractmethod
    def read_directory(self, directory_path: str) -> List[Document]:
        """Read all supported files from a directory recursively."""
        pass

    @abstractmethod
    def read_file(self, file_path: str) -> Document:
        """Read a single file."""
        pass


class IVisionAnalyzer(ABC):
    """Interface for analyzing images and diagrams."""

    @abstractmethod
    def analyze_image(self, image_path: str) -> str:
        """Analyze an image and return a comprehensive description."""
        pass

    @abstractmethod
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from an image using OCR."""
        pass

    @abstractmethod
    def generate_summary(self, image_path: str) -> str:
        """Generate a comprehensive summary of an image or diagram."""
        pass


class IDocumentChunker(ABC):
    """Interface for chunking documents."""

    @abstractmethod
    def chunk_document(self, document: Document) -> List[Chunk]:
        """Chunk a document into smaller pieces."""
        pass

    @abstractmethod
    def chunk_documents(self, documents: List[Document]) -> List[Chunk]:
        """Chunk multiple documents."""
        pass


class IEmbeddingService(ABC):
    """Interface for creating embeddings."""

    @abstractmethod
    def create_embedding(self, text: str) -> List[float]:
        """Create an embedding for a text."""
        pass

    @abstractmethod
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts."""
        pass


class IVectorStore(ABC):
    """Interface for vector storage operations."""

    @abstractmethod
    def initialize_collection(self) -> None:
        """Initialize the vector collection."""
        pass

    @abstractmethod
    def insert_embeddings(self, embedded_chunks: List[EmbeddedChunk]) -> None:
        """Insert embeddings into the vector store."""
        pass

    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[dict]:
        """Search for similar embeddings."""
        pass

    @abstractmethod
    def delete_collection(self) -> None:
        """Delete the collection."""
        pass

    @abstractmethod
    def collection_exists(self) -> bool:
        """Check if collection exists."""
        pass

    @abstractmethod
    def get_existing_file_paths(self) -> set:
        """Get set of file paths that already exist in the collection."""
        pass

    @abstractmethod
    def get_document_count(self) -> int:
        """Get total number of documents in collection."""
        pass

    @abstractmethod
    def initialize_or_load_collection(self) -> None:
        """Initialize collection if it doesn't exist, or load existing one."""
        pass

