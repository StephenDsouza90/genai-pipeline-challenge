"""
Image analysis and ingredient detection using OpenAI Vision API.

This module provides functionality to analyze food images and extract visible
ingredients using OpenAI's vision models for recipe recommendation purposes.
"""

import base64
import io

from openai import OpenAI
from PIL import Image

from src.ai.prompts import AIPrompts
from src.config import Settings
from src.constants import BULLET_POINT_CHARS, MINIMUM_INGREDIENT_LENGTH
from src.utils.logger import Logger


class ImageVisionService:
    """
    Service for analyzing images and extracting food ingredients using OpenAI Vision API.
    """

    def __init__(self, settings: Settings, logger: Logger):
        """
        Initialize the image vision service.

        Args:
            settings (Settings): Application settings containing OpenAI API key.
        """
        self.settings = settings
        self.logger = logger
        self.client = OpenAI(api_key=settings.openai_api_key)

    def extract_ingredients_from_image(self, image_data: bytes) -> list[str]:
        """
        Extract ingredients from an uploaded image using OpenAI Vision API.

        Args:
            image_data (bytes): The image file data as bytes.

        Returns:
            list[str]: List of detected ingredients.
        """
        try:
            image_base64 = base64.b64encode(image_data).decode(self.settings.file_encoding)

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": AIPrompts.VISION_INGREDIENT_EXTRACTION_PROMPT,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                                "detail": self.settings.vision_image_detail,
                            },
                        },
                    ],
                },
            ]

            response = self.client.chat.completions.create(
                model=self.settings.openai_chat_model,
                messages=messages,
                max_tokens=self.settings.vision_max_tokens,
                temperature=self.settings.vision_temperature,
            )

            content = response.choices[0].message.content
            if not content:
                return []

            ingredients = []
            for line in content.strip().split("\n"):
                ingredient = line.strip()
                ingredient = ingredient.lstrip(BULLET_POINT_CHARS)
                if ingredient and len(ingredient) > MINIMUM_INGREDIENT_LENGTH:
                    ingredients.append(ingredient)

            return ingredients

        except Exception as e:
            self.logger.error(f"Error extracting ingredients from image: {e}")
            return []

    def validate_image(self, image_data: bytes) -> bool:
        """
        Validate that the uploaded file is a valid image.

        Args:
            image_data (bytes): The image file data as bytes.

        Returns:
            bool: True if the image is valid, False otherwise.
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            return image.format in self.settings.vision_supported_formats
        except Exception as e:
            self.logger.error(f"Error validating image: {e}")
            return False
