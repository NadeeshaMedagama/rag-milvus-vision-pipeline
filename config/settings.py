"""Configuration module for the RAG application."""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Azure OpenAI Configuration
    azure_openai_api_key: str = Field(..., alias="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: str = Field(..., alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_deployment_name: str = Field(..., alias="AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_openai_api_version: str = Field(default="2024-02-15-preview", alias="AZURE_OPENAI_API_VERSION")
    azure_openai_embedding_deployment: str = Field(..., alias="AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

    # Milvus Cloud Configuration
    milvus_uri: str = Field(..., alias="MILVUS_URI")
    milvus_token: str = Field(..., alias="MILVUS_TOKEN")
    milvus_user: str = Field(default="", alias="MILVUS_USER")
    milvus_password: str = Field(default="", alias="MILVUS_PASSWORD")
    milvus_collection_name: str = Field(default="readme_embeddings", alias="MILVUS_COLLECTION_NAME")

    # GitHub Repository Configuration
    github_repo_url: str = Field(..., alias="GITHUB_REPO_URL")
    github_token: str = Field(default="", alias="GITHUB_TOKEN")

    # Application Configuration
    chunk_size: int = Field(default=1000, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, alias="CHUNK_OVERLAP")
    embedding_dimension: int = Field(default=1536, alias="EMBEDDING_DIMENSION")

    # Google Vision API Configuration
    google_application_credentials: str = Field(..., alias="GOOGLE_APPLICATION_CREDENTIALS")
    google_vision_max_results: int = Field(default=10, alias="GOOGLE_VISION_MAX_RESULTS")

    # Local Data Directory Configuration
    data_directory: str = Field(default="./data/diagrams", alias="DATA_DIRECTORY")
    process_local_files: bool = Field(default=True, alias="PROCESS_LOCAL_FILES")

    # Processing Control Configuration
    skip_existing_documents: bool = Field(default=True, alias="SKIP_EXISTING_DOCUMENTS")
    force_reprocess: bool = Field(default=False, alias="FORCE_REPROCESS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()

