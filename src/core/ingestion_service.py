"""
Recipe data ingestion and parsing service.

This module provides functionality to parse recipe text content, extract
structured data (title, ingredients, instructions), and store recipes
in the database with generated embeddings.
"""

import re
from typing import Optional

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

    def ingest_recipe(self, content: str) -> Optional[Recipe]:
        """
        Ingest a recipe into the database.

        Args:
            content (str): The content to ingest.

        Returns:
            Recipe: The ingested recipe.
        """
        try:
            parsed_recipe = self.parse_content(content)
            if not parsed_recipe:
                self.logger.error("Failed to parse recipe content")
                return None

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
            return None

    def parse_content(self, content: str) -> Optional[Recipe]:
        """
        Parse recipe content and extract title, ingredients, and instructions.

        Args:
            content (str): The content to parse.

        Returns:
            Optional[Recipe]: The parsed recipe data.
        """
        content = content.strip()

        title = self._extract_title(content)
        if not title:
            self.logger.error("Failed to extract recipe title")
            return None

        ingredients = self._extract_ingredients(content)
        if not ingredients:
            self.logger.error("Failed to extract ingredients")
            return None

        instructions = self._extract_instructions(content)
        if not instructions:
            self.logger.error("Failed to extract instructions")
            return None

        return Recipe(title=title, ingredients=ingredients, instructions=instructions)

    def _extract_title(self, content: str) -> Optional[str]:
        """
        Extract recipe title from content.

        Args:
            content (str): The content to extract the title from.

        Returns:
            Optional[str]: The recipe title.
        """
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.lower().startswith(
                (RECIPE_SECTIONS["INGREDIENTS"], RECIPE_SECTIONS["INSTRUCTIONS"])
            ):
                return line
        return None

    def _extract_ingredients(self, content: str) -> Optional[str]:
        """
        Extract ingredients section from content.

        Args:
            content (str): The content to extract the ingredients from.

        Returns:
            Optional[str]: The ingredients.
        """
        ingredients_pattern = re.compile(
            r"Ingredients:\s*\n(.*?)(?=\n\s*Instructions:|$)", re.DOTALL | re.IGNORECASE
        )
        match = ingredients_pattern.search(content)
        if match:
            ingredients_text = match.group(1).strip()
            # Clean up the ingredients text
            ingredients_lines = []
            for line in ingredients_text.split("\n"):
                line = line.strip()
                if line:
                    ingredients_lines.append(line)
            return "\n".join(ingredients_lines)
        return None

    def _extract_instructions(self, content: str) -> Optional[str]:
        """
        Extract instructions section from content.

        Args:
            content (str): The content to extract the instructions from.

        Returns:
            Optional[str]: The instructions.
        """
        instructions_pattern = re.compile(
            r"Instructions:\s*\n(.*?)$", re.DOTALL | re.IGNORECASE
        )
        match = instructions_pattern.search(content)
        if match:
            instructions_text = match.group(1).strip()
            # Clean up the instructions text
            instructions_lines = []
            for line in instructions_text.split("\n"):
                line = line.strip()
                if line:
                    instructions_lines.append(line)
            return "\n".join(instructions_lines)
        return None
