"""Azure OpenAI embedding service implementation."""
from typing import List
from openai import AzureOpenAI

from interfaces import IEmbeddingService


class AzureOpenAIEmbeddingService(IEmbeddingService):
    """Service for creating embeddings using Azure OpenAI."""

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        deployment_name: str,
        api_version: str = "2024-02-15-preview"
    ):
        """
        Initialize the Azure OpenAI embedding service.

        Args:
            api_key: Azure OpenAI API key
            endpoint: Azure OpenAI endpoint
            deployment_name: Deployment name for embeddings
            api_version: API version
        """
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        self.deployment_name = deployment_name

    def create_embedding(self, text: str) -> List[float]:
        """
        Create an embedding for a text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        # Replace newlines with spaces for better embeddings
        text = text.replace("\n", " ")

        response = self.client.embeddings.create(
            input=[text],
            model=self.deployment_name
        )

        return response.data[0].embedding

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        # Replace newlines with spaces
        texts = [text.replace("\n", " ") for text in texts]

        # Azure OpenAI has a limit on batch size, process in batches
        batch_size = 16
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.embeddings.create(
                input=batch,
                model=self.deployment_name
            )
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
            print(f"Created embeddings for batch {i // batch_size + 1}/{(len(texts) - 1) // batch_size + 1}")

        return all_embeddings

