from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

from src.config import Settings
from src.data.models import Recipe


class RecipeRAGPipeline:
    """
    RAG (Retrieval-Augmented Generation) pipeline for recipe recommendations using Haystack.
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize the RAG pipeline.
        
        Args:
            settings (Settings): Application settings containing OpenAI configuration.
        """
        self.settings = settings
        self._setup_pipeline()
    
    def _setup_pipeline(self):
        """
        Set up the RAG pipeline with prompt builder and chat generator.
        """
        # Define the chef prompt template
        template = [
            ChatMessage.from_system(
                """You are a professional chef with extensive knowledge of cooking and recipes. 
                You help people create delicious meals using the ingredients they have available.
                
                When given a list of ingredients and some recipe context, you should:
                1. Suggest recipes that can be made with the available ingredients
                2. Provide clear, step-by-step cooking instructions
                3. Offer helpful cooking tips and variations
                4. Be encouraging and enthusiastic about cooking
                5. If the ingredients don't match the provided recipes exactly, suggest creative adaptations
                
                Always format your response in Markdown for better readability."""
            ),
            ChatMessage.from_user(
                """Based on the following recipe database entries:

                {% for recipe in recipes %}
                **{{ recipe.title }}**
                Ingredients: {{ recipe.ingredients }}
                Instructions: {{ recipe.instructions }}
                
                {% endfor %}

                Available ingredients: {{ ingredients }}
                
                Please recommend recipes I can make with these ingredients. If none of the database recipes match exactly, suggest creative adaptations or new recipes using the available ingredients."""
            )
        ]
        
        self.prompt_builder = ChatPromptBuilder(template=template)
        self.chat_generator = OpenAIChatGenerator(
            api_key=Secret.from_token(self.settings.openai_api_key),
            model=self.settings.openai_chat_model,
            generation_kwargs={"max_tokens": 1000, "temperature": 0.7}
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
        result = self.pipeline.run({
            "prompt_builder": {
                "recipes": recipes,
                "ingredients": ingredients
            }
        })
        
        return result["chat_generator"]["replies"][0].text if result and "chat_generator" in result and "replies" in result["chat_generator"] else "I apologize, but I'm having trouble generating a recipe recommendation at the moment. Please try again later."
    