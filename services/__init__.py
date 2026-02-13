"""Services package."""
# Lazy imports to avoid loading unnecessary dependencies
# gitpython requires git executable which may not be available in all environments

def __getattr__(name):
    """Lazy import to avoid loading git dependency when not needed."""
    if name == "GitHubRepositoryReader":
        from .repository_reader import GitHubRepositoryReader
        return GitHubRepositoryReader
    elif name == "DocumentChunker":
        from .document_chunker import DocumentChunker
        return DocumentChunker
    elif name == "AzureOpenAIEmbeddingService":
        from .embedding_service import AzureOpenAIEmbeddingService
        return AzureOpenAIEmbeddingService
    elif name == "MilvusVectorStore":
        from .vector_store import MilvusVectorStore
        return MilvusVectorStore
    elif name == "GoogleVisionAnalyzer":
        from .vision_analyzer import GoogleVisionAnalyzer
        return GoogleVisionAnalyzer
    elif name == "LocalFileReader":
        from .local_file_reader import LocalFileReader
        return LocalFileReader
    elif name == "URLContentReader":
        from .url_content_reader import URLContentReader
        return URLContentReader
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "GitHubRepositoryReader",
    "DocumentChunker",
    "AzureOpenAIEmbeddingService",
    "MilvusVectorStore",
    "GoogleVisionAnalyzer",
    "LocalFileReader",
    "URLContentReader"
]

