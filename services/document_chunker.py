"""Document chunking service implementation."""
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter

from interfaces import IDocumentChunker
from models import Document, Chunk


class DocumentChunker(IDocumentChunker):
    """Service for chunking documents into smaller pieces."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the document chunker.

        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def chunk_document(self, document: Document) -> List[Chunk]:
        """
        Chunk a document into smaller pieces.

        Args:
            document: Document to chunk

        Returns:
            List of Chunk objects
        """
        chunks = []
        text_chunks = self.text_splitter.split_text(document.content)

        for idx, text_chunk in enumerate(text_chunks):
            chunk = Chunk(
                content=text_chunk,
                chunk_index=idx,
                source_file_path=document.file_path,
                repository_url=document.repository_url,
                document_type=document.document_type,
                metadata={
                    **document.metadata,
                    "total_chunks": len(text_chunks)
                }
            )
            chunks.append(chunk)

        return chunks

    def chunk_documents(self, documents: List[Document]) -> List[Chunk]:
        """
        Chunk multiple documents.

        Args:
            documents: List of documents to chunk

        Returns:
            List of all chunks from all documents
        """
        all_chunks = []

        for document in documents:
            chunks = self.chunk_document(document)
            all_chunks.extend(chunks)
            print(f"Chunked {document.file_path}: {len(chunks)} chunks")

        print(f"Total chunks created: {len(all_chunks)}")
        return all_chunks

