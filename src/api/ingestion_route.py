"""
Recipe ingestion API endpoints.

This module defines FastAPI routes for ingesting recipe data from uploaded
text files, with proper validation, error handling, and batch processing
capabilities.
"""

from fastapi import APIRouter, File, UploadFile, status

from src.api.schemas import IngestRecipeResponse, RecipeResponse, IngestRecipesResponse
from src.config import Settings
from src.core.ingestion_service import IngestionService
from src.utils.logger import Logger


class IngestionRoutes:
    """
    This class defines the API routes for the Ingestion application.
    """

    def __init__(
        self, ingestion_service: IngestionService, logger: Logger, settings: Settings
    ):
        """
        Initialize the IngestionRoutes class.

        Args:
            ingestion_service (IngestionService): The ingestion service to use.
            logger (Logger): The logger instance.
            settings (Settings): The settings instance.
        """
        self.ingestion_service = ingestion_service
        self.logger = logger
        self.settings = settings
        self.router = APIRouter(tags=["Ingestion"])
        self.setup_routes()

    def setup_routes(self):
        @self.router.post(
            "/ingest-recipes",
            status_code=status.HTTP_200_OK,
            summary="Ingest multiple recipes into the database",
            description="Ingest multiple recipes into the database",
            response_model=IngestRecipesResponse,
            response_description="Ingest multiple recipes into the database",
        )
        async def ingest_recipes(
            files: list[UploadFile] = File(..., description="TXT files to import"),
        ):
            """
            Ingest multiple recipes into the database.

            Args:
                files (list[UploadFile]): The files to ingest.

            Returns:
                IngestRecipesResponse: The response containing the ingested recipes.

            Raises:
                HTTPException: If the ingestion service fails.
            """
            self.logger.info(f"Ingesting {len(files)} recipes")

            resp = []
            for file in files:
                try:
                    content = await file.read()
                    recipe = self.ingestion_service.ingest_recipe(
                        content.decode("utf-8")
                    )

                    recipe_response = RecipeResponse(
                        id=recipe.id,
                        title=recipe.title,
                        ingredients=recipe.ingredients,
                        instructions=recipe.instructions,
                        # embedding=recipe.embedding, # NOTE: We don't need to return the embedding for now
                        created_at=recipe.created_at.isoformat()
                        if recipe.created_at
                        else None,
                        updated_at=recipe.updated_at.isoformat()
                        if recipe.updated_at
                        else None,
                    )

                    resp.append(
                        IngestRecipeResponse(
                            success=True, recipe=recipe_response, error=None
                        )
                    )

                except Exception as e:
                    self.logger.error(
                        f"Error ingesting recipe from file {file.filename}: {e}"
                    )
                    resp.append(
                        IngestRecipeResponse(success=False, recipe=None, error=str(e))
                    )

            self.logger.info(f"Processed {len(resp)} recipes")
            return IngestRecipesResponse(recipes=resp)
