from src.data.repository import Repository
from ai.embedding import EmbeddingService
from ai.rag import RecipeRAGPipeline


class RecommendationService:
    """
    Service class for recommending recipes using RAG (Retrieval-Augmented Generation).
    """
    
    def __init__(self, repository: Repository, embedding_service: EmbeddingService, rag_pipeline: RecipeRAGPipeline):
        """
        Initialize the recommendation service.

        Args:
            repository (Repository): The repository.
            embedding_service (EmbeddingService): The embedding service.
            rag_pipeline (RecipeRAGPipeline): The RAG pipeline for generating recommendations.
        """
        self.repository = repository
        self.embedding_service = embedding_service
        self.rag_pipeline = rag_pipeline

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
