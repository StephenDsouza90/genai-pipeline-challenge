"""
Recipe data ingestion and parsing service.

This module provides functionality to parse recipe text content, extract
structured data (title, ingredients, instructions), and store recipes
in the database with generated embeddings.
"""

import re

from src.constants import RECIPE_SECTIONS
from src.data.repository import Repository
from src.data.models import Recipe
from src.ai.embedding import EmbeddingService
from src.utils.logger import Logger


class IngestionService:
    """
    Service class for ingesting recipe data into the database.
    """

    def __init__(
        self,
        repository: Repository,
        embedding_service: EmbeddingService,
        logger: Logger,
    ):
        """
        Initialize the ingestion service.

        Args:
            repository (Repository): The repository.
            embedding_service (EmbeddingService): The embedding service for generating embeddings.
        """
        self.repository = repository
        self.embedding_service = embedding_service
        self.logger = logger

    def ingest_recipe(self, content: str) -> Recipe:
        """
        Ingest a recipe into the database.

        Args:
            content (str): The content to ingest.

        Returns:
            Recipe: The ingested recipe.

        Raises:
            Exception: If the recipe ingestion fails.
        """
        try:
            parsed_recipe = self.parse_content(content)

            if self.repository.exists_by_title(parsed_recipe.title):
                self.logger.info(f"Recipe already exists: {parsed_recipe.title}")
                return self.repository.get_by_title(parsed_recipe.title)

            parsed_recipe.embedding = self.embedding_service.generate_recipe_embedding(
                title=parsed_recipe.title,
                ingredients=parsed_recipe.ingredients,
                instructions=parsed_recipe.instructions,
            )

            return self.repository.create(parsed_recipe)
        except Exception as e:
            self.logger.error(f"Error ingesting recipe: {e}")
            raise Exception(f"Error ingesting recipe: {e}")

    def parse_content(self, content: str) -> Recipe:
        """
        Parse recipe content and extract title, ingredients, and instructions.

        Args:
            content (str): The content to parse.

        Returns:
            Recipe: The parsed recipe data.

        Raises:
            Exception: If the recipe parsing fails.
        """
        content = content.strip()

        title = self._extract_title(content)
        if not title:
            self.logger.error("Failed to extract recipe title")
            raise Exception("Failed to extract recipe title")

        ingredients = self._extract_ingredients(content)
        if not ingredients:
            self.logger.error("Failed to extract ingredients")
            raise Exception("Failed to extract ingredients")

        instructions = self._extract_instructions(content)
        if not instructions:
            self.logger.error("Failed to extract instructions")
            raise Exception("Failed to extract instructions")

        return Recipe(title=title, ingredients=ingredients, instructions=instructions)

    def _extract_title(self, content: str) -> str | None:
        """
        Extract recipe title from content.

        Args:
            content (str): The content to extract the title from.

        Returns:
            str | None: The recipe title.
        """
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.lower().startswith(
                (RECIPE_SECTIONS["INGREDIENTS"], RECIPE_SECTIONS["INSTRUCTIONS"])
            ):
                return line
        return None

    def _extract_ingredients(self, content: str) -> str | None:
        """
        Extract ingredients section from content.

        Args:
            content (str): The content to extract the ingredients from.

        Returns:
            str | None: The ingredients.
        """
        ingredients_pattern = re.compile(
            r"Ingredients:\s*\n(.*?)(?=\n\s*Instructions:|$)", re.DOTALL | re.IGNORECASE
        )
        match = ingredients_pattern.search(content)
        if match:
            ingredients_text = match.group(1).strip()
            ingredients_lines = []
            for line in ingredients_text.split("\n"):
                line = line.strip()
                if line:
                    ingredients_lines.append(line)
            return "\n".join(ingredients_lines)
        return None

    def _extract_instructions(self, content: str) -> str | None:
        """
        Extract instructions section from content.

        Args:
            content (str): The content to extract the instructions from.

        Returns:
            str | None: The instructions.
        """
        instructions_pattern = re.compile(
            r"Instructions:\s*\n(.*?)$", re.DOTALL | re.IGNORECASE
        )
        match = instructions_pattern.search(content)
        if match:
            instructions_text = match.group(1).strip()
            instructions_lines = []
            for line in instructions_text.split("\n"):
                line = line.strip()
                if line:
                    instructions_lines.append(line)
            return "\n".join(instructions_lines)
        return None
