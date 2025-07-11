"""
Application configuration settings using Pydantic BaseSettings.

This module defines all configurable settings for the application, including
database configuration, AI model parameters, API settings, and error messages.
Settings can be overridden using environment variables.
"""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    """

    # Database configuration
    database_url: str = os.getenv("DB_URL", "")
    database_pool_recycle: int = 300
    database_max_retries: int = 5
    database_retry_delay: int = 2

    # OpenAI configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_chat_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"

    # AI Model Parameters
    embedding_dimensions: int = 1536

    # Vision Service Configuration
    vision_max_tokens: int = 500
    vision_temperature: float = 0.3
    vision_image_detail: str = "high"
    vision_supported_formats: list[str] = ["JPEG", "PNG", "WEBP", "GIF"]

    # RAG Pipeline Configuration
    rag_max_tokens: int = 1000
    rag_temperature: float = 0.7

    # Search Configuration
    default_search_limit: int = 5
    recommendation_search_limit: int = 3

    # Application configuration
    app_name: str = "What's for Dinner?"
    app_description: str = "Let's find a recipe for you based on the ingredients you have for tonight's dinner."
    app_version: str = "1.0.0"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"

    # API Configuration
    api_prefix: str = "/api/v1"

    # File System Configuration
    data_zip_filename: str = "data.zip"
    recipes_directory: str = "data/recipes"
    recipe_file_extension: str = ".txt"
    file_encoding: str = "utf-8"

    # Startup Data Loading Configuration
    load_startup_data: bool = True

    # Error Messages
    generic_error_message: str = "I apologize, but I'm having trouble processing your request at the moment. Please try again later."
    recipe_recommendation_error: str = "I apologize, but I'm having trouble generating a recipe recommendation at the moment. Please try again later."
    recipe_ingestion_error: str = "I apologize, but I'm having trouble ingesting recipes at the moment. Please try again later."
