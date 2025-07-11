import io
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.core.recommendation_service import RecommendationService
from src.api.recommendation_route import RecommendationRoutes
from src.data.repository import Repository
from src.utils.logger import Logger
from src.ai.embedding import EmbeddingService
from src.ai.rag import RecipeRAGPipeline
from src.ai.vision import ImageVisionService
from src.config import Settings


@pytest.fixture
def mock_logger():
    """Mock the logger."""
    mock = MagicMock(spec=Logger)
    mock.info = MagicMock()
    mock.error = MagicMock()
    return mock


@pytest.fixture
def mock_repository():
    """Mock the repository."""
    return MagicMock(spec=Repository)


@pytest.fixture
def mock_recommendation_service():
    """Mock the recommendation service."""
    return MagicMock(spec=RecommendationService)


@pytest.fixture
def mock_embedding_service():
    """Mock the embedding service."""
    return MagicMock(spec=EmbeddingService)


@pytest.fixture
def mock_rag_pipeline():
    """Mock the RAG pipeline."""
    return MagicMock(spec=RecipeRAGPipeline)


@pytest.fixture
def mock_vision_service():
    """Mock the vision service."""
    return MagicMock(spec=ImageVisionService)


@pytest.fixture
def mock_settings():
    """Mock the settings."""
    settings = MagicMock(spec=Settings)
    settings.recipe_recommendation_error = "Error recommending recipe"
    return settings


@pytest.fixture
def test_app(mock_recommendation_service, mock_logger, mock_settings):
    """Test the app."""
    recommendation_routes = RecommendationRoutes(
        mock_recommendation_service, mock_logger, mock_settings
    )

    app = FastAPI()
    app.include_router(recommendation_routes.router)

    return app


@pytest.fixture
def client(test_app):
    """Create a test client for the FastAPI app."""
    return TestClient(test_app)


def test_recommend_recipe_success(client, mock_recommendation_service):
    """Test successful recipe recommendation with ingredients."""
    ingredients = ["tomatoes", "basil", "mozzarella"]
    expected_recipe = "Caprese Salad: Mix tomatoes, basil, and mozzarella..."
    mock_recommendation_service.recommend_recipe.return_value = expected_recipe

    response = client.post("/recommend-recipe", json={"ingredients": ingredients})

    assert response.status_code == 200
    assert response.json() == {"recipe": expected_recipe}
    mock_recommendation_service.recommend_recipe.assert_called_once_with(ingredients)


def test_recommend_recipe_empty_ingredients(client, mock_recommendation_service):
    """Test recipe recommendation with empty ingredients list."""
    ingredients = []
    # The service should raise a ValueError for empty ingredients
    mock_recommendation_service.recommend_recipe.side_effect = ValueError(
        "Ingredients cannot be empty"
    )

    response = client.post("/recommend-recipe", json={"ingredients": ingredients})

    assert response.status_code == 400
    assert response.json() == {"detail": "Ingredients cannot be empty"}
    mock_recommendation_service.recommend_recipe.assert_called_once_with(ingredients)


def test_recommend_recipe_service_error(client, mock_recommendation_service):
    """Test recipe recommendation when service raises an exception."""
    ingredients = ["tomatoes", "basil"]
    mock_recommendation_service.recommend_recipe.side_effect = Exception(
        "Service error"
    )

    response = client.post("/recommend-recipe", json={"ingredients": ingredients})

    assert response.status_code == 500
    assert response.json() == {
        "detail": "An unexpected error occurred while processing your request. Please try again later."
    }


def test_recommend_recipe_invalid_request_body(client):
    """Test recipe recommendation with invalid request body."""
    response = client.post("/recommend-recipe", json={"invalid_field": "value"})

    assert response.status_code == 422


def test_recommend_recipe_from_image_success(client, mock_recommendation_service):
    """Test successful recipe recommendation from image."""
    detected_ingredients = ["carrots", "onions", "celery"]
    expected_recipe = "Vegetable Soup: Chop carrots, onions, and celery..."
    mock_recommendation_service.recommend_recipe_from_image.return_value = (
        detected_ingredients,
        expected_recipe,
    )

    image_data = b"fake image data"
    image_file = io.BytesIO(image_data)

    response = client.post(
        "/recommend-recipe-from-image",
        files={"image": ("test_image.jpg", image_file, "image/jpeg")},
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["detected_ingredients"] == detected_ingredients
    assert response_data["recipe"] == expected_recipe
    mock_recommendation_service.recommend_recipe_from_image.assert_called_once_with(
        image_data
    )


def test_recommend_recipe_from_image_invalid_content_type(client):
    """Test recipe recommendation from image with invalid content type."""
    text_file = io.BytesIO(b"not an image")

    response = client.post(
        "/recommend-recipe-from-image",
        files={"image": ("test.txt", text_file, "text/plain")},
    )

    assert response.status_code == 400
    assert (
        "Invalid file type. Please upload an image file." in response.json()["detail"]
    )


def test_recommend_recipe_from_image_no_content_type(client):
    """Test recipe recommendation from image with no content type."""
    image_file = io.BytesIO(b"fake image data")

    response = client.post(
        "/recommend-recipe-from-image",
        files={"image": ("test_image.jpg", image_file, None)},
    )

    assert response.status_code == 400
    assert (
        "Invalid file type. Please upload an image file." in response.json()["detail"]
    )


def test_recommend_recipe_from_image_service_error(client, mock_recommendation_service):
    """Test recipe recommendation from image when service raises an exception."""
    mock_recommendation_service.recommend_recipe_from_image.side_effect = Exception(
        "Service error"
    )
    image_data = b"fake image data"
    image_file = io.BytesIO(image_data)

    response = client.post(
        "/recommend-recipe-from-image",
        files={"image": ("test_image.jpg", image_file, "image/jpeg")},
    )

    assert response.status_code == 500
    assert (
        "An unexpected error occurred while processing your request. Please try again later."
        in response.json()["detail"]
    )


def test_recommend_recipe_from_image_missing_file(client):
    """Test recipe recommendation from image without uploading a file."""
    response = client.post("/recommend-recipe-from-image")

    assert response.status_code == 422


def test_recommend_recipe_from_image_multiple_formats(
    client, mock_recommendation_service
):
    """Test recipe recommendation from image with different image formats."""
    detected_ingredients = ["apples", "cinnamon"]
    expected_recipe = "Apple Pie: Mix apples with cinnamon..."
    mock_recommendation_service.recommend_recipe_from_image.return_value = (
        detected_ingredients,
        expected_recipe,
    )

    image_formats = [
        ("test.jpg", "image/jpeg"),
        ("test.png", "image/png"),
        ("test.webp", "image/webp"),
        ("test.gif", "image/gif"),
    ]

    for filename, content_type in image_formats:
        image_data = b"fake image data"
        image_file = io.BytesIO(image_data)

        response = client.post(
            "/recommend-recipe-from-image",
            files={"image": (filename, image_file, content_type)},
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["detected_ingredients"] == detected_ingredients
        assert response_data["recipe"] == expected_recipe
