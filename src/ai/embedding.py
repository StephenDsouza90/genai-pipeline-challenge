"""
Text embedding generation service using OpenAI embeddings.

This module provides functionality to generate vector embeddings for recipes
and text queries using OpenAI's text-embedding models through the Haystack framework.
"""

from haystack.components.embedders import OpenAITextEmbedder
from haystack.utils import Secret

from src.config import Settings
from src.utils.logger import Logger


class EmbeddingService:
    """
    Service for generating text embeddings using Haystack and OpenAI.
    """

    def __init__(self, settings: Settings, logger: Logger):
        """
        Initialize the embedding service.

        Args:
            settings (Settings): Application settings containing OpenAI API key.
        """
        self.settings = settings
        self.logger = logger
        self.embedder = OpenAITextEmbedder(
            api_key=Secret.from_token(settings.openai_api_key),
            model=settings.openai_embedding_model,
            dimensions=settings.embedding_dimensions,
        )

    def generate_recipe_embedding(
        self, title: str, ingredients: str, instructions: str
    ) -> list[float] | None:
        """
        Generate embedding for a recipe by combining title, ingredients, and instructions.

        Args:
            title (str): Recipe title
            ingredients (str): Recipe ingredients
            instructions (str): Recipe instructions

        Returns:
            list[float] | None: The embedding vector or None if generation fails.
        """
        try:
            combined_text = f"Title: {title}\n\nIngredients:\n{ingredients}\n\nInstructions:\n{instructions}"
            result = self.embedder.run(text=combined_text)
            return result["embedding"] if result and "embedding" in result else None

        except Exception as e:
            self.logger.error(f"Error generating recipe embedding: {e}")
            return None

    def generate_text_embedding(self, text: str) -> list[float] | None:
        """
        Generate embedding for any text.

        Args:
            text (str): The text to embed.

        Returns:
            list[float] | None: The embedding vector or None if generation fails.
        """
        try:
            result = self.embedder.run(text=text)
            return result["embedding"] if result and "embedding" in result else None

        except Exception as e:
            self.logger.error(f"Error generating text embedding: {e}")
            return None
