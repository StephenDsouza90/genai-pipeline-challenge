from fastapi import APIRouter, HTTPException, File, UploadFile, status

from src.api.schemas import IngestRecipeResponse, RecipeResponse, IngestRecipesResponse
from src.core.ingestion_service import IngestionService
from src.utils.logger import Logger


class IngestionRoutes:
    """
    This class defines the API routes for the Ingestion application.
    """

    def __init__(self, ingestion_service: IngestionService, logger: Logger):
        """
        Initialize the IngestionRoutes class.

        Args:
            ingestion_service (IngestionService): The ingestion service to use.
        """
        self.ingestion_service = ingestion_service
        self.logger = logger
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
            """
            try:
                self.logger.info(f"Ingesting {len(files)} recipes")

                resp = []
                for file in files:
                    content = await file.read()
                    recipe = self.ingestion_service.ingest_recipe(content.decode('utf-8'))
                    if recipe is None:
                        self.logger.error(f"Failed to ingest recipe: {file.filename}")
                        resp.append(IngestRecipeResponse(success=False, recipe=None, error="Failed to ingest recipe"))
                    else:
                        self.logger.info(f"Ingested recipe: {file.filename}")
                        recipe_response = RecipeResponse(
                            id=recipe.id,
                            title=recipe.title,
                            ingredients=recipe.ingredients,
                            instructions=recipe.instructions,
                            # embedding=recipe.embedding, # NOTE: We don't need to return the embedding for now
                            created_at=recipe.created_at.isoformat() if recipe.created_at else None,
                            updated_at=recipe.updated_at.isoformat() if recipe.updated_at else None
                        )
                        resp.append(IngestRecipeResponse(success=True, recipe=recipe_response))

                self.logger.info(f"Ingested {len(resp)} recipes")
            except Exception as e:
                self.logger.error(f"Error ingesting recipes: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="I apologize, but I'm having trouble ingesting recipes at the moment. Please try again later."
                )
            
            return IngestRecipesResponse(recipes=resp)
