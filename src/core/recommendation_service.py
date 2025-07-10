from src.data.repository import Repository
from src.ai.embedding import EmbeddingService
from src.ai.rag import RecipeRAGPipeline
from src.ai.vision import ImageVisionService


class RecommendationService:
    """
    Service class for recommending recipes using RAG (Retrieval-Augmented Generation).
    """
    
    def __init__(self, repository: Repository, embedding_service: EmbeddingService, rag_pipeline: RecipeRAGPipeline, vision_service: ImageVisionService):
        """
        Initialize the recommendation service.

        Args:
            repository (Repository): The repository.
            embedding_service (EmbeddingService): The embedding service.
            rag_pipeline (RecipeRAGPipeline): The RAG pipeline for generating recommendations.
            vision_service (ImageVisionService): The vision service for image analysis.
        """
        self.repository = repository
        self.embedding_service = embedding_service
        self.rag_pipeline = rag_pipeline
        self.vision_service = vision_service

    def recommend_recipe(self, ingredients: list[str]) -> str:
        """
        Recommend a recipe based on the ingredients provided using RAG.

        Args:
            ingredients (list[str]): The ingredients to recommend a recipe for.

        Returns:
            str: The recommended recipe in Markdown format.
        """
        ingredients_text = ", ".join(ingredients)
        
        query_embedding = self.embedding_service.generate_text_embedding(ingredients_text)
        
        similar_recipes = self.repository.search_by_embedding(query_embedding, limit=3)

        if not similar_recipes:
            # TODO : Implement this
            pass

        return self.rag_pipeline.generate_recommendation(similar_recipes, ingredients_text)

    def recommend_recipe_from_image(self, image_data: bytes) -> tuple[list[str], str]:
        """
        Recommend a recipe based on ingredients detected in an uploaded image.

        Args:
            image_data (bytes): The image file data as bytes.

        Returns:
            tuple[list[str], str]: A tuple containing the detected ingredients and the recommended recipe.
        """
        if not self.vision_service.validate_image(image_data):
            return [], "Invalid image format. Please upload a valid image file (JPEG, PNG, WEBP, or GIF)."
        
        detected_ingredients = self.vision_service.extract_ingredients_from_image(image_data)
        
        if not detected_ingredients:
            return [], "No ingredients could be detected in the image. Please try uploading a clearer image with visible food ingredients."
        
        recipe = self.recommend_recipe(detected_ingredients)
        
        return detected_ingredients, recipe
