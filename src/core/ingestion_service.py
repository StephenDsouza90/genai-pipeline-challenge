import re
from typing import Optional

from src.data.repository import Repository
from src.data.models import Recipe
from ai.embedding import EmbeddingService


class IngestionService:
    """
    Service class for ingesting recipe data into the database.
    """
    
    def __init__(self, repository: Repository, embedding_service: EmbeddingService):
        """
        Initialize the ingestion service.

        Args:
            repository (Repository): The repository.
            embedding_service (EmbeddingService): The embedding service for generating embeddings.
        """
        self.repository = repository
        self.embedding_service = embedding_service

    def ingest_recipe(self, content: str) -> Optional[Recipe]:
        """
        Ingest a recipe into the database.

        Args:
            content (str): The content to ingest.

        Returns:
            Recipe: The ingested recipe.
        """
        parsed_recipe = self.parse_content(content)
        if not parsed_recipe:
            return None
        
        if self.repository.exists_by_title(parsed_recipe.title):
            return self.repository.get_by_title(parsed_recipe.title)
        
        parsed_recipe.embedding = self.embedding_service.generate_recipe_embedding(
            title=parsed_recipe.title,
            ingredients=parsed_recipe.ingredients,
            instructions=parsed_recipe.instructions
        )
        
        return self.repository.create(parsed_recipe)
    
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
            return None
        
        ingredients = self._extract_ingredients(content)
        if not ingredients:
            return None
        
        instructions = self._extract_instructions(content)
        if not instructions:
            return None
        
        return Recipe(
            title=title,
            ingredients=ingredients,
            instructions=instructions
        )

    def _extract_title(self, content: str) -> Optional[str]:
        """
        Extract recipe title from content.

        Args:
            content (str): The content to extract the title from.

        Returns:
            Optional[str]: The recipe title.
        """
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.lower().startswith(('ingredients:', 'instructions:')):
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
        ingredients_pattern = re.compile(r'Ingredients:\s*\n(.*?)(?=\n\s*Instructions:|$)', re.DOTALL | re.IGNORECASE)
        match = ingredients_pattern.search(content)
        if match:
            ingredients_text = match.group(1).strip()
            # Clean up the ingredients text
            ingredients_lines = []
            for line in ingredients_text.split('\n'):
                line = line.strip()
                if line:
                    ingredients_lines.append(line)
            return '\n'.join(ingredients_lines)
        return None
    
    def _extract_instructions(self, content: str) -> Optional[str]:
        """
        Extract instructions section from content.

        Args:
            content (str): The content to extract the instructions from.

        Returns:
            Optional[str]: The instructions.
        """
        instructions_pattern = re.compile(r'Instructions:\s*\n(.*?)$', re.DOTALL | re.IGNORECASE)
        match = instructions_pattern.search(content)
        if match:
            instructions_text = match.group(1).strip()
            # Clean up the instructions text
            instructions_lines = []
            for line in instructions_text.split('\n'):
                line = line.strip()
                if line:
                    instructions_lines.append(line)
            return '\n'.join(instructions_lines)
        return None
