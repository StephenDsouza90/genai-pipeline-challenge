"""
AI prompts used throughout the application.
"""

from haystack.dataclasses import ChatMessage


class AIPrompts:
    """
    Centralized AI prompts for the application.
    """

    RAG_SYSTEM_PROMPT = """You are a professional chef with extensive knowledge of cooking and recipes. 
You help people create delicious meals using the ingredients they have available.

When given a list of ingredients and some recipe context, you should:
1. Suggest recipes that can be made with the available ingredients
2. Provide clear, step-by-step cooking instructions
3. Offer helpful cooking tips and variations
4. Be encouraging and enthusiastic about cooking
5. If the ingredients don't match the provided recipes exactly, suggest creative adaptations

Always format your response in Markdown for better readability."""

    RAG_USER_PROMPT = """Based on the following recipe database entries:

{% for recipe in recipes %}
**{{ recipe.title }}**
Ingredients: {{ recipe.ingredients }}
Instructions: {{ recipe.instructions }}

{% endfor %}

Available ingredients: {{ ingredients }}

Please recommend recipes I can make with these ingredients. If none of the database recipes match exactly, suggest creative adaptations or new recipes using the available ingredients."""

    VISION_INGREDIENT_EXTRACTION_PROMPT = """Analyze this image and identify all visible food ingredients. 
Return ONLY a simple list of ingredients, one per line, without any additional text, bullets, or formatting. 
Focus on identifying specific ingredients like vegetables, fruits, proteins, oils, spices, etc. 
If you see packaged items, try to identify the actual ingredient (e.g., 'flour' instead of 'flour bag').
Be specific but concise (e.g., 'red bell pepper' instead of just 'pepper')."""

    @classmethod
    def get_rag_template(cls) -> list[ChatMessage]:
        """
        Get the RAG pipeline chat template.

        Returns:
            list[ChatMessage]: The chat template for the RAG pipeline.
        """
        return [
            ChatMessage.from_system(cls.RAG_SYSTEM_PROMPT),
            ChatMessage.from_user(cls.RAG_USER_PROMPT),
        ]
