"""Data models for the RAG application."""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum


class DocumentType(Enum):
    """Type of document."""
    MARKDOWN = "markdown"
    IMAGE = "image"
    DIAGRAM = "diagram"
    SPREADSHEET = "spreadsheet"
    WORD_DOCUMENT = "word_document"
    DRAWIO = "drawio"


@dataclass
class Document:
    """Represents a document."""
    content: str
    file_path: str
    repository_url: str
    document_type: DocumentType = DocumentType.MARKDOWN
    metadata: Optional[dict] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Chunk:
    """Represents a document chunk."""
    content: str
    chunk_index: int
    source_file_path: str
    repository_url: str
    document_type: DocumentType = DocumentType.MARKDOWN
    metadata: Optional[dict] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class EmbeddedChunk:
    """Represents a chunk with its embedding."""
    chunk: Chunk
    embedding: List[float]
    embedding_id: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class WorkflowState:
    """State for the LangGraph workflow."""
    repository_url: str
    documents: List[Document] = None
    chunks: List[Chunk] = None
    embedded_chunks: List[EmbeddedChunk] = None
    error: Optional[str] = None
    status: str = "initialized"

    def __post_init__(self):
        if self.documents is None:
            self.documents = []
        if self.chunks is None:
            self.chunks = []
        if self.embedded_chunks is None:
            self.embedded_chunks = []

