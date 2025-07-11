import re

import pytest
import httpx


BASE_URL = "http://localhost:8000"
TIMEOUT = 60.0


@pytest.mark.asyncio
async def test_recommend_recipe_from_text_success():
    """
    Test that the recommendation API returns a success response.
    """
    body = {
        "ingredients": [
            "chicken",
            "mixed vegetables",
            "soy sauce",
            "vegetable oil",
            "clove garlic",
        ]
    }
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
        response = await client.post("/api/v1/recommend-recipe", json=body)
        response_data = response.json()
        recipe_content = response_data["recipe"]
        recipe_lower = recipe_content.lower()

        assert response.status_code == 200
        assert "recipe" in response_data
        assert "quick chicken stir-fry" in recipe_content.lower()
        assert "chicken" in recipe_lower
        assert "mixed vegetables" in recipe_lower or "vegetables" in recipe_lower
        assert "soy sauce" in recipe_lower
        assert "vegetable oil" in recipe_lower or "oil" in recipe_lower
        assert "garlic" in recipe_lower


@pytest.mark.asyncio
async def test_recommend_recipe_from_image_success():
    """
    Test that the recommendation API returns a success response.
    """
    files = [
        (
            "image",
            ("food1.webp", open("tests/assets/photos/food1.webp", "rb"), "image/webp"),
        )
    ]
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
        response = await client.post("/api/v1/recommend-recipe-from-image", files=files)
        response_data = response.json()
        detected_ingredients = response_data["detected_ingredients"]
        recipe_content = response_data["recipe"]
        markdown_parts = re.findall(r"#|\*|\*\*|\n", recipe_content)

        assert response.status_code == 200
        assert "detected_ingredients" in response_data
        assert "recipe" in response_data
        assert isinstance(detected_ingredients, list)
        assert len(detected_ingredients) > 0
        assert isinstance(recipe_content, str)
        assert len(recipe_content) > 0
        assert len(markdown_parts) > 0
