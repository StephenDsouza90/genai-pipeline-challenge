from fastapi import APIRouter, status, File, UploadFile, HTTPException

from src.api.schemas import RecommendRecipeRequest, RecommendRecipeResponse, RecommendRecipeFromImageResponse
from src.core.recommendation_service import RecommendationService


class RecommendationRoutes:
    """
    This class defines the API routes for the AI Recipe Generator application.
    """

    def __init__(self, recommendation_service: RecommendationService):
        """
        Initialize the Routes class.

        Args:
            recommendation_service (RecommendationService): The recommendation service to use.
        """
        self.recommendation_service = recommendation_service
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
            response = self.recommendation_service.recommend_recipe(request.ingredients)
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
            image: UploadFile = File(..., description="Image file containing food ingredients")
        ):
            """
            Recommend a recipe based on ingredients detected in an uploaded image.

            Args:
                image (UploadFile): The uploaded image file containing food ingredients.

            Returns:
                RecommendRecipeFromImageResponse: The response containing detected ingredients and recommended recipe.
            """
            if not image.content_type or not image.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file type. Please upload an image file."
                )
            
            try:
                image_data = await image.read()
            except Exception:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to read the uploaded image file."
                )
            
            detected_ingredients, recipe = self.recommendation_service.recommend_recipe_from_image(image_data)
            
            return RecommendRecipeFromImageResponse(
                detected_ingredients=detected_ingredients,
                recipe=recipe
            )
