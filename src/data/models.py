"""
Database models and schemas.

This module defines SQLAlchemy models for the application's data structures,
including the Recipe model with vector embedding support for similarity search.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime
from pgvector.sqlalchemy import Vector

from src.data.base import Base
from src.config import Settings


settings = Settings()


class Recipe(Base):
    """
    Recipe model with vector embedding support.

    Args:
        id (int): The ID of the recipe.
        title (str): The title of the recipe.
        ingredients (str): The ingredients of the recipe.
        instructions (str): The instructions of the recipe.
        embedding (Vector): The embedding of the recipe.
        created_at (datetime): The creation date of the recipe.
    """

    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    ingredients = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)
    embedding = Column(Vector(settings.embedding_dimensions))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
