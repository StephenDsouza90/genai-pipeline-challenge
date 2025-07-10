"""
FastAPI application configuration and initialization.

This module provides the API class that configures and initializes the FastAPI
application with proper metadata, middleware, and settings.
"""

from fastapi import FastAPI

from src.config import Settings


class API:
    """
    Client initializes and configures the FastAPI application.
    """

    def __init__(self, lifespan, settings: Settings):
        """
        Initialize the FastAPI application with OpenAPI metadata.
        Optionally, CORS middleware can be added to the app, if needed.

        Args:
            lifespan: Lifespan context manager for the FastAPI app.
            settings: Settings object containing application settings.
        """
        self.app = FastAPI(
            title=settings.app_name,
            description=settings.app_description,
            version=settings.app_version,
            docs_url=settings.docs_url,
            redoc_url=settings.redoc_url,
            openapi_url=settings.openapi_url,
            lifespan=lifespan,
        )
