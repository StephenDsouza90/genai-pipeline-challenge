"""
RAG (Retrieval-Augmented Generation) pipeline for recipe recommendations.

This module implements a RAG pipeline using Haystack to generate personalized
recipe recommendations based on available ingredients and retrieved recipe data.
"""

from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.utils import Secret

from src.ai.prompts import AIPrompts
from src.config import Settings
from src.data.models import Recipe
from src.utils.logger import Logger


class RecipeRAGPipeline:
    """
    RAG (Retrieval-Augmented Generation) pipeline for recipe recommendations using Haystack.
    """

    def __init__(self, settings: Settings, logger: Logger):
        """
        Initialize the RAG pipeline.

        Args:
            settings (Settings): Application settings containing OpenAI configuration.
        """
        self.settings = settings
        self.logger = logger
        self._setup_pipeline()

    def _setup_pipeline(self):
        """
        Set up the RAG pipeline with prompt builder and chat generator.
        """
        template = AIPrompts.get_rag_template()

        self.prompt_builder = ChatPromptBuilder(template=template)
        self.chat_generator = OpenAIChatGenerator(
            api_key=Secret.from_token(self.settings.openai_api_key),
            model=self.settings.openai_chat_model,
            generation_kwargs={
                "max_tokens": self.settings.rag_max_tokens,
                "temperature": self.settings.rag_temperature,
            },
        )

        self.pipeline = Pipeline()
        self.pipeline.add_component("prompt_builder", self.prompt_builder)
        self.pipeline.add_component("chat_generator", self.chat_generator)
        self.pipeline.connect("prompt_builder.prompt", "chat_generator.messages")

    def generate_recommendation(self, recipes: list[Recipe], ingredients: str) -> str:
        """
        Generate a recipe recommendation using the RAG pipeline.

        Args:
            recipes (list[Recipe]): List of retrieved recipe objects from the database.
            ingredients (str): Comma-separated string of available ingredients.

        Returns:
            str: Generated recipe recommendation in Markdown format.
        """
        try:
            result = self.pipeline.run(
                {"prompt_builder": {"recipes": recipes, "ingredients": ingredients}}
            )

            return (
                result["chat_generator"]["replies"][0].text
                if result
                and "chat_generator" in result
                and "replies" in result["chat_generator"]
                else self.settings.recipe_recommendation_error
            )
        except Exception as e:
            self.logger.error(f"Error generating recipe recommendation: {e}")
            return self.settings.recipe_recommendation_error
