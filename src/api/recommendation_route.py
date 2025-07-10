"""
Recipe recommendation API endpoints.

This module defines FastAPI routes for recipe recommendations, including
text-based ingredient input and image-based ingredient detection with
proper error handling and response formatting.
"""

from fastapi import APIRouter, status, File, UploadFile, HTTPException

from src.api.schemas import (
    RecommendRecipeRequest,
    RecommendRecipeResponse,
    RecommendRecipeFromImageResponse,
)
from src.config import Settings
from src.constants import IMAGE_CONTENT_TYPE_PREFIX
from src.core.recommendation_service import RecommendationService
from src.utils.logger import Logger


class RecommendationRoutes:
    """
    This class defines the API routes for the AI Recipe Generator application.
    """

    def __init__(
        self,
        recommendation_service: RecommendationService,
        logger: Logger,
        settings: Settings,
    ):
        """
        Initialize the Routes class.

        Args:
            recommendation_service (RecommendationService): The recommendation service to use.
            logger (Logger): The logger instance.
            settings (Settings): The settings instance.
        """
        self.recommendation_service = recommendation_service
        self.logger = logger
        self.settings = settings
        self.router = APIRouter(tags=["Recommendation"])
        self.setup_routes()

    def setup_routes(self):
        @self.router.post(
            "/recommend-recipe",
            status_code=status.HTTP_200_OK,
            summary="Recommend a recipe based on the ingredients provided",
            description="Recommend a recipe based on the ingredients provided",
            response_model=RecommendRecipeResponse,
            response_description="Recommend a recipe based on the ingredients provided",
        )
        async def recommend_recipe(request: RecommendRecipeRequest):
            """
            Recommend a recipe based on the ingredients provided.

            Args:
                request (RecommendRecipeRequest): The request containing the ingredients to recommend a recipe for.

            Returns:
                RecommendRecipeResponse: The response containing the recommended recipe.
            """
            try:
                self.logger.info(f"Recommend recipe request: {request.ingredients}")

                response = self.recommendation_service.recommend_recipe(
                    request.ingredients
                )

                self.logger.info(f"Recommend recipe response: {response}")
            except Exception as e:
                self.logger.error(f"Error recommending recipe: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=self.settings.recipe_recommendation_error,
                )
            return RecommendRecipeResponse(recipe=response)

        @self.router.post(
            "/recommend-recipe-from-image",
            status_code=status.HTTP_200_OK,
            summary="Recommend a recipe based on ingredients detected in an uploaded image",
            description="Upload an image containing food ingredients and get recipe recommendations based on AI-detected ingredients",
            response_model=RecommendRecipeFromImageResponse,
            response_description="Recipe recommendation based on ingredients detected in the image",
        )
        async def recommend_recipe_from_image(
            image: UploadFile = File(
                ..., description="Image file containing food ingredients"
            ),
        ):
            """
            Recommend a recipe based on ingredients detected in an uploaded image.

            Args:
                image (UploadFile): The uploaded image file containing food ingredients.

            Returns:
                RecommendRecipeFromImageResponse: The response containing detected ingredients and recommended recipe.
            """
            try:
                self.logger.info(f"Image content type: {image.content_type}")

                if not image.content_type or not image.content_type.startswith(
                    IMAGE_CONTENT_TYPE_PREFIX
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid file type. Please upload an image file.",
                    )

                image_data = await image.read()
                detected_ingredients, recipe = (
                    self.recommendation_service.recommend_recipe_from_image(image_data)
                )

                self.logger.info(f"Detected ingredients: {detected_ingredients}")
                self.logger.info(f"Recipe: {recipe}")

            except Exception as e:
                self.logger.error(f"Error reading image: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to read the uploaded image file.",
                )

            return RecommendRecipeFromImageResponse(
                detected_ingredients=detected_ingredients, recipe=recipe
            )
