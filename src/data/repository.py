"""
Data access layer for recipe operations.

This module provides repository pattern implementation for recipe data access,
including CRUD operations and vector similarity search functionality.
"""

from sqlalchemy import text

from src.config import Settings
from src.data.database import DatabaseManager
from src.data.decorator import handle_session
from src.data.models import Recipe
from src.utils.logger import Logger


class Repository:
    """
    Repository class for database operations.
    """

    def __init__(self, db_manager: DatabaseManager, logger: Logger, settings: Settings):
        """
        Initialize repository with database session.

        Args:
            db_manager (DatabaseManager): The database manager.
            logger (Logger): The logger instance.
            settings (Settings): The settings instance.
        """
        self.db_manager = db_manager
        self.logger = logger
        self.settings = settings

    @handle_session
    def create(self, session, recipe: Recipe) -> Recipe:
        """
        Create a new recipe in the database.

        Args:
            recipe (Recipe): The recipe to create.

        Returns:
            Recipe: The created recipe.
        """
        session.add(recipe)
        session.commit()
        session.refresh(recipe)
        return recipe

    @handle_session
    def get_by_title(self, session, title: str) -> Recipe | None:
        """
        Get recipe by title.

        Args:
            title (str): The recipe title.

        Returns:
            Recipe | None: The recipe if found, None otherwise.
        """
        return session.query(Recipe).filter(Recipe.title == title).first()

    @handle_session
    def exists_by_title(self, session, title: str) -> bool:
        """
        Check if recipe exists by title.

        Args:
            title (str): The recipe title.

        Returns:
            bool: True if recipe exists, False otherwise.
        """
        return session.query(Recipe).filter(Recipe.title == title).first() is not None

    @handle_session
    def search_by_embedding(
        self, session, embedding: list[float], limit: int | None = None
    ) -> list[Recipe]:
        """
        Search for recipes using vector similarity.

        Args:
            embedding (list[float]): The query embedding vector.
            limit (int): Maximum number of results to return.

        Returns:
            list[Recipe]: List of similar recipes ordered by similarity.
        """
        if not embedding:
            return []

        limit = limit or self.settings.default_search_limit

        query = text("""
            SELECT * FROM recipes 
            WHERE embedding IS NOT NULL 
            ORDER BY embedding <=> :embedding 
            LIMIT :limit
        """)

        result = session.execute(query, {"embedding": str(embedding), "limit": limit})
        rows = result.fetchall()

        return [
            Recipe(
                id=row.id,
                title=row.title,
                ingredients=row.ingredients,
                instructions=row.instructions,
                embedding=row.embedding,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]
