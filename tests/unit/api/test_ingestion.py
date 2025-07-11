import io
from unittest.mock import MagicMock
from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.core.ingestion_service import IngestionService
from src.api.ingestion_route import IngestionRoutes
from src.data.repository import Repository
from src.data.models import Recipe
from src.utils.logger import Logger
from src.ai.embedding import EmbeddingService
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
def mock_embedding_service():
    """Mock the embedding service."""
    return MagicMock(spec=EmbeddingService)


@pytest.fixture
def mock_ingestion_service():
    """Mock the ingestion service."""
    return MagicMock(spec=IngestionService)


@pytest.fixture
def mock_settings():
    """Mock the settings."""
    settings = MagicMock(spec=Settings)
    settings.recipe_ingestion_error = "Error ingesting recipe"
    return settings


@pytest.fixture
def test_app(mock_ingestion_service, mock_logger, mock_settings):
    """Create a test FastAPI app with ingestion routes."""
    ingestion_routes = IngestionRoutes(
        mock_ingestion_service, mock_logger, mock_settings
    )

    app = FastAPI()
    app.include_router(ingestion_routes.router)

    return app


@pytest.fixture
def client(test_app):
    """Create a test client for the FastAPI app."""
    return TestClient(test_app)


@pytest.fixture
def sample_recipe():
    """Create a sample recipe for testing."""
    return Recipe(
        id=1,
        title="Test Recipe",
        ingredients="2 cups flour\n1 cup sugar\n3 eggs",
        instructions="1. Mix flour and sugar\n2. Add eggs\n3. Bake at 350°F",
        embedding=[0.1, 0.2, 0.3],
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        updated_at=datetime(2024, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def sample_recipe_content():
    """Create sample recipe content for testing."""
    return """Test Recipe

Ingredients:
2 cups flour
1 cup sugar
3 eggs

Instructions:
1. Mix flour and sugar
2. Add eggs
3. Bake at 350°F for 30 minutes"""


def test_ingest_recipes_success_single_file(
    client, mock_ingestion_service, sample_recipe, sample_recipe_content
):
    """Test successful ingestion of a single recipe file."""
    mock_ingestion_service.ingest_recipe.return_value = sample_recipe

    recipe_file = io.BytesIO(sample_recipe_content.encode("utf-8"))

    response = client.post(
        "/ingest-recipes",
        files={"files": ("test_recipe.txt", recipe_file, "text/plain")},
    )

    assert response.status_code == 200
    response_data = response.json()
    assert "recipes" in response_data
    assert len(response_data["recipes"]) == 1

    recipe_response = response_data["recipes"][0]
    assert recipe_response["success"] is True
    assert recipe_response["recipe"]["id"] == 1
    assert recipe_response["recipe"]["title"] == "Test Recipe"
    assert (
        recipe_response["recipe"]["ingredients"] == "2 cups flour\n1 cup sugar\n3 eggs"
    )
    assert (
        recipe_response["recipe"]["instructions"]
        == "1. Mix flour and sugar\n2. Add eggs\n3. Bake at 350°F"
    )
    assert recipe_response["error"] is None

    mock_ingestion_service.ingest_recipe.assert_called_once_with(sample_recipe_content)


def test_ingest_recipes_success_multiple_files(
    client, mock_ingestion_service, sample_recipe_content
):
    """Test successful ingestion of multiple recipe files."""
    recipe1 = Recipe(
        id=1,
        title="Recipe 1",
        ingredients="Ingredient 1",
        instructions="Step 1",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
    )
    recipe2 = Recipe(
        id=2,
        title="Recipe 2",
        ingredients="Ingredient 2",
        instructions="Step 2",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
    )

    mock_ingestion_service.ingest_recipe.side_effect = [recipe1, recipe2]

    file1 = io.BytesIO(sample_recipe_content.encode("utf-8"))
    file2 = io.BytesIO(sample_recipe_content.encode("utf-8"))

    response = client.post(
        "/ingest-recipes",
        files=[
            ("files", ("recipe1.txt", file1, "text/plain")),
            ("files", ("recipe2.txt", file2, "text/plain")),
        ],
    )

    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data["recipes"]) == 2

    assert response_data["recipes"][0]["success"] is True
    assert response_data["recipes"][0]["recipe"]["id"] == 1
    assert response_data["recipes"][0]["recipe"]["title"] == "Recipe 1"

    assert response_data["recipes"][1]["success"] is True
    assert response_data["recipes"][1]["recipe"]["id"] == 2
    assert response_data["recipes"][1]["recipe"]["title"] == "Recipe 2"

    assert mock_ingestion_service.ingest_recipe.call_count == 2


def test_ingest_recipes_service_exception(
    client, mock_ingestion_service, sample_recipe_content
):
    """Test ingestion when service raises an exception."""
    mock_ingestion_service.ingest_recipe.side_effect = Exception("Service error")

    recipe_file = io.BytesIO(sample_recipe_content.encode("utf-8"))

    response = client.post(
        "/ingest-recipes",
        files={"files": ("test_recipe.txt", recipe_file, "text/plain")},
    )

    assert response.status_code == 200
    response_data = response.json()
    assert "recipes" in response_data
    assert len(response_data["recipes"]) == 1
    
    recipe_response = response_data["recipes"][0]
    assert recipe_response["success"] is False
    assert recipe_response["recipe"] is None
    assert recipe_response["error"] == "Service error"


def test_ingest_recipes_empty_file_list(client):
    """Test ingestion with no files provided."""
    response = client.post("/ingest-recipes")

    assert response.status_code == 422


def test_ingest_recipes_invalid_file_encoding(client, mock_ingestion_service):
    """Test ingestion with invalid file encoding."""
    mock_ingestion_service.ingest_recipe.side_effect = UnicodeDecodeError(
        "utf-8", b"invalid", 0, 1, "invalid start byte"
    )

    invalid_file = io.BytesIO(b"\xff\xfe\x00\x00invalid content")

    response = client.post(
        "/ingest-recipes", files={"files": ("invalid.txt", invalid_file, "text/plain")}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert "recipes" in response_data
    assert len(response_data["recipes"]) == 1
    
    recipe_response = response_data["recipes"][0]
    assert recipe_response["success"] is False
    assert recipe_response["recipe"] is None
    assert "invalid start byte" in recipe_response["error"]


def test_ingest_recipes_response_format(
    client, mock_ingestion_service, sample_recipe, sample_recipe_content
):
    """Test that the response format matches the expected schema."""
    mock_ingestion_service.ingest_recipe.return_value = sample_recipe

    recipe_file = io.BytesIO(sample_recipe_content.encode("utf-8"))

    response = client.post(
        "/ingest-recipes",
        files={"files": ("test_recipe.txt", recipe_file, "text/plain")},
    )

    assert response.status_code == 200
    response_data = response.json()

    assert "recipes" in response_data
    assert isinstance(response_data["recipes"], list)

    recipe_response = response_data["recipes"][0]
    required_fields = ["success", "recipe", "error"]
    for field in required_fields:
        assert field in recipe_response

    recipe_obj = recipe_response["recipe"]
    recipe_fields = [
        "id",
        "title",
        "ingredients",
        "instructions",
        "created_at",
        "updated_at",
    ]
    for field in recipe_fields:
        assert field in recipe_obj

    assert isinstance(recipe_response["success"], bool)
    assert isinstance(recipe_obj["id"], int)
    assert isinstance(recipe_obj["title"], str)
    assert isinstance(recipe_obj["ingredients"], str)
    assert isinstance(recipe_obj["instructions"], str)
