from fastapi import APIRouter, status

from src.api.schemas import RecommendRecipeRequest, RecommendRecipeResponse
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
