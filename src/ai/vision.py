import base64
import io

from openai import OpenAI
from PIL import Image

from src.config import Settings


class ImageVisionService:
    """
    Service for analyzing images and extracting food ingredients using OpenAI Vision API.
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize the image vision service.
        
        Args:
            settings (Settings): Application settings containing OpenAI API key.
        """
        self.settings = settings
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
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this image and identify all visible food ingredients. 
                            Return ONLY a simple list of ingredients, one per line, without any additional text, bullets, or formatting. 
                            Focus on identifying specific ingredients like vegetables, fruits, proteins, oils, spices, etc. 
                            If you see packaged items, try to identify the actual ingredient (e.g., 'flour' instead of 'flour bag').
                            Be specific but concise (e.g., 'red bell pepper' instead of just 'pepper')."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                                "detail": "high",
                            },
                        }
                    ],
                },
            ]
            
            response = self.client.chat.completions.create(
                model=self.settings.openai_chat_model,
                messages=messages,
                max_tokens=500,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            if not content:
                return []
            
            ingredients = []
            for line in content.strip().split('\n'):
                ingredient = line.strip()
                ingredient = ingredient.lstrip('•-*1234567890. ')
                if ingredient and len(ingredient) > 1:
                    ingredients.append(ingredient)
            
            return ingredients
            
        except Exception as e:
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
            return image.format in ['JPEG', 'PNG', 'WEBP', 'GIF']
        except Exception:
            return False 