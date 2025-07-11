import pytest
import httpx


BASE_URL = "http://localhost:8000"
TIMEOUT = 60.0


@pytest.mark.asyncio
async def test_ingested_recipes_success():
    """Test that the ingestion API returns a success response."""
    files = [
        ("files", ("01.txt", open("tests/assets/recipes/01.txt", "rb"), "text/plain")),
        ("files", ("02.txt", open("tests/assets/recipes/02.txt", "rb"), "text/plain")),
        ("files", ("06.txt", open("tests/assets/recipes/06.txt", "rb"), "text/plain")),
    ]
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
        response = await client.post("/api/v1/ingest-recipes", files=files)
        assert response.status_code == 200

        # 01.txt
        assert (
            response.json()["recipes"][0]["recipe"]["title"] == "Quick Chicken Stir-Fry"
        )
        assert (
            response.json()["recipes"][0]["recipe"]["ingredients"]
            == "2 chicken breasts, diced\n1 cup mixed vegetables\n2 tbsp soy sauce\n1 tbsp vegetable oil\n1 clove garlic, minced"
        )
        assert (
            response.json()["recipes"][0]["recipe"]["instructions"]
            == "Heat oil in a wok over medium-high heat.\nAdd garlic and chicken, cook until chicken is nearly done.\nAdd vegetables and stir-fry for 2-3 minutes.\nPour in soy sauce, cook for another minute.\nServe hot over rice."
        )
        assert response.json()["recipes"][0]["recipe"]["embedding"] is None
        assert response.json()["recipes"][0]["recipe"]["created_at"] is not None
        assert response.json()["recipes"][0]["recipe"]["updated_at"] is not None
        assert response.json()["recipes"][0]["error"] is None

        # 02.txt
        assert response.json()["recipes"][1]["recipe"]["title"] == "Easy Tomato Pasta"
        assert (
            response.json()["recipes"][1]["recipe"]["ingredients"]
            == "8 oz pasta\n1 can diced tomatoes\n2 tbsp olive oil\n1 tsp dried basil\nSalt and pepper to taste\nGrated Parmesan cheese"
        )
        assert (
            response.json()["recipes"][1]["recipe"]["instructions"]
            == "Cook pasta according to package instructions.\nIn a pan, heat olive oil and add diced tomatoes.\nSimmer for 5 minutes, add basil, salt, and pepper.\nDrain pasta and toss with the tomato sauce.\nServe with grated Parmesan on top."
        )
        assert response.json()["recipes"][1]["recipe"]["embedding"] is None
        assert response.json()["recipes"][1]["recipe"]["created_at"] is not None
        assert response.json()["recipes"][1]["recipe"]["updated_at"] is not None
        assert response.json()["recipes"][1]["error"] is None

        # 06.txt
        assert (
            response.json()["recipes"][2]["recipe"]["title"] == "Quick Vegetable Soup"
        )
        assert (
            response.json()["recipes"][2]["recipe"]["ingredients"]
            == "4 cups vegetable broth\n1 can mixed vegetables, drained\n1 can diced tomatoes\n1 onion, chopped\n2 cloves garlic, minced\n1 tsp dried thyme\nSalt and pepper to taste"
        )
        assert (
            response.json()["recipes"][2]["recipe"]["instructions"]
            == "In a large pot, sauté onion and garlic until softened.\nAdd broth, mixed vegetables, tomatoes, and thyme.\nBring to a boil, then simmer for 15 minutes.\nSeason with salt and pepper.\nServe hot, optionally with crusty bread."
        )
        assert response.json()["recipes"][2]["recipe"]["embedding"] is None
        assert response.json()["recipes"][2]["recipe"]["created_at"] is not None
        assert response.json()["recipes"][2]["recipe"]["updated_at"] is not None
        assert response.json()["recipes"][2]["error"] is None
