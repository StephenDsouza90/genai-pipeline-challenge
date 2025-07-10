from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import Settings
from src.api.recommendation_route import RecommendationRoutes
from src.api.ingestion_route import IngestionRoutes
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
    db_manager = DatabaseManager(settings)
    db_manager.bootstrap()

    repository = Repository(db_manager)
    app.state.repository = repository


def init_services(app: FastAPI, settings: Settings):
    """
    Initialize the services.

    Args:
        app (FastAPI): The FastAPI application instance.
        settings (Settings): The settings for the application.
    """
    embedding_service = EmbeddingService(settings)
    app.state.embedding_service = embedding_service

    rag_pipeline = RecipeRAGPipeline(settings)
    app.state.rag_pipeline = rag_pipeline

    vision_service = ImageVisionService(settings)
    app.state.vision_service = vision_service

    ingestion_service = IngestionService(app.state.repository, app.state.embedding_service)
    app.state.ingestion_service = ingestion_service

    recommendation_service = RecommendationService(app.state.repository, app.state.embedding_service, app.state.rag_pipeline, app.state.vision_service)
    app.state.recommendation_service = recommendation_service


def init_routes(app: FastAPI):
    """
    Initialize the API routes.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    recommendation_routes = RecommendationRoutes(app.state.recommendation_service)
    app.include_router(recommendation_routes.router, prefix="/api/v1")

    ingestion_routes = IngestionRoutes(app.state.ingestion_service)
    app.include_router(ingestion_routes.router, prefix="/api/v1")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application, initializing async resources on startup.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        settings = Settings()

        init_logger(app)

        init_db(app, settings)

        init_services(app, settings)

        init_routes(app)

        yield

        app.state.db_manager.close()

    return API(lifespan=lifespan).app
