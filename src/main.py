"""
Main application entry point and initialization.

This module handles the FastAPI application creation, service initialization,
database setup, and startup data loading. It serves as the central orchestrator
for the What's for Dinner recipe recommendation application.
"""

import zipfile
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from src.config import Settings
from src.api.recommendation_route import RecommendationRoutes
from src.api.ingestion_route import IngestionRoutes
from src.api.health_route import HealthRoutes
from src.api.client import API
from src.data.database import DatabaseManager
from src.data.repository import Repository
from src.core.ingestion_service import IngestionService
from src.core.recommendation_service import RecommendationService
from src.ai.embedding import EmbeddingService
from src.ai.rag import RecipeRAGPipeline
from src.ai.vision import ImageVisionService
from src.utils.logger import Logger


def init_logger(app: FastAPI):
    """
    Initialize the logger.

    Args:
        app (FastAPI, optional): The FastAPI application instance. Defaults to None.
    """
    logger = Logger().get_logger()
    app.state.logger = logger


def init_db(app: FastAPI, settings: Settings):
    """
    Initialize the database.

    Args:
        app (FastAPI): The FastAPI application instance.
        settings (Settings): The settings for the application.
    """
    db_manager = DatabaseManager(settings, app.state.logger)
    db_manager.bootstrap()
    app.state.db_manager = db_manager

    repository = Repository(app.state.db_manager, app.state.logger, settings)
    app.state.repository = repository


def init_services(app: FastAPI, settings: Settings):
    """
    Initialize the services.

    Args:
        app (FastAPI): The FastAPI application instance.
        settings (Settings): The settings for the application.
    """
    embedding_service = EmbeddingService(settings, app.state.logger)
    app.state.embedding_service = embedding_service

    rag_pipeline = RecipeRAGPipeline(settings, app.state.logger)
    app.state.rag_pipeline = rag_pipeline

    vision_service = ImageVisionService(settings, app.state.logger)
    app.state.vision_service = vision_service

    ingestion_service = IngestionService(
        app.state.repository, app.state.embedding_service, app.state.logger
    )
    app.state.ingestion_service = ingestion_service

    recommendation_service = RecommendationService(
        app.state.repository,
        app.state.embedding_service,
        app.state.rag_pipeline,
        app.state.vision_service,
        app.state.logger,
    )
    app.state.recommendation_service = recommendation_service


def init_routes(app: FastAPI, settings: Settings):
    """
    Initialize the API routes.

    Args:
        app (FastAPI): The FastAPI application instance.
        settings (Settings): The settings for the application.
    """
    recommendation_routes = RecommendationRoutes(
        app.state.recommendation_service, app.state.logger, settings
    )
    app.include_router(recommendation_routes.router, prefix=settings.api_prefix)

    ingestion_routes = IngestionRoutes(
        app.state.ingestion_service, app.state.logger, settings
    )
    app.include_router(ingestion_routes.router, prefix=settings.api_prefix)

    health_routes = HealthRoutes()
    app.include_router(health_routes.router)


def load_startup_data(app: FastAPI):
    """
    Load recipe data from local files during app startup.

    Checks for data.zip first, then falls back to data/recipes folder.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    logger = app.state.logger
    ingestion_service = app.state.ingestion_service

    success_count = 0
    error_count = 0

    settings = app.state.settings
    data_zip_path = Path(settings.data_zip_filename)
    recipes_dir_path = Path(settings.recipes_directory)

    if data_zip_path.exists():
        logger.info("Found data.zip file, extracting and loading recipes...")
        try:
            with zipfile.ZipFile(data_zip_path, "r") as zip_file:
                for file_info in zip_file.infolist():
                    if (
                        file_info.filename.endswith(settings.recipe_file_extension)
                        and not file_info.is_dir()
                    ):
                        try:
                            content = zip_file.read(file_info.filename).decode(
                                settings.file_encoding
                            )
                            recipe = ingestion_service.ingest_recipe(content)
                            if recipe:
                                success_count += 1
                                logger.info(
                                    f"Successfully ingested recipe: {recipe.title}"
                                )
                            else:
                                error_count += 1
                                logger.warning(
                                    f"Failed to parse recipe from {file_info.filename}"
                                )
                        except Exception as e:
                            error_count += 1
                            logger.error(
                                f"Error processing {file_info.filename}: {str(e)}"
                            )
        except Exception as e:
            logger.error(f"Error reading data.zip file: {str(e)}")

    elif recipes_dir_path.exists() and recipes_dir_path.is_dir():
        logger.info("Loading recipes from data/recipes folder...")

        recipe_files = list(recipes_dir_path.glob(f"*{settings.recipe_file_extension}"))

        if not recipe_files:
            logger.warning(
                f"No {settings.recipe_file_extension} files found in {settings.recipes_directory} folder"
            )
            return

        for recipe_file in sorted(recipe_files):
            try:
                content = recipe_file.read_text(encoding=settings.file_encoding)
                recipe = ingestion_service.ingest_recipe(content)
                if recipe:
                    success_count += 1
                    logger.info(f"Successfully ingested recipe: {recipe.title}")
                else:
                    error_count += 1
                    logger.warning(f"Failed to parse recipe from {recipe_file.name}")
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing {recipe_file.name}: {str(e)}")

    else:
        logger.warning(
            f"No {settings.data_zip_filename} file or {settings.recipes_directory} folder found for startup data loading"
        )
        return

    total_processed = success_count + error_count
    if total_processed > 0:
        logger.info(
            f"Startup data loading completed: {success_count} successful, {error_count} errors out of {total_processed} files processed"
        )
    else:
        logger.warning("No recipes were processed during startup data loading")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application, initializing async resources on startup.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        settings = Settings()
        app.state.settings = settings

        init_logger(app)

        init_db(app, settings)

        init_services(app, settings)

        init_routes(app, settings)

        if settings.load_startup_data:
            load_startup_data(app)
        else:
            app.state.logger.info("Startup data loading disabled by configuration")

        app.state.logger.info("App initialized")

        yield

        app.state.logger.info("App shutdown")

        app.state.db_manager.close()

    settings = Settings()
    return API(lifespan=lifespan, settings=settings).app
