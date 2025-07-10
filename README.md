# GenAI Pipeline Challenge

## Challenge Overview
This project is a proof-of-concept AI-powered recipe recommendation system. It provides recipe suggestions based on a list of ingredients (text or image) using Retrieval-Augmented Generation (RAG) with OpenAI's GPT-4o and Haystack. The backend is built with FastAPI, and recipes are stored in a Postgres database with vector search support.

---

## Architecture
- **FastAPI**: Serves as the web API framework.
- **RAG Pipeline (Haystack + OpenAI)**: Retrieves relevant recipes and generates recommendations using GPT-4o.
- **Postgres + pgvector**: Stores recipes and supports vector similarity search for ingredient matching.
- **Image Vision**: Extracts ingredients from uploaded images using OpenAI's vision models.
- **Self-contained Services**: Each major part (database, ingestion, recommendation, vision, embedding) is implemented as a self-contained service. All services are initialized in `main.py` and injected via dependency injection, making the code modular and easy to extend or test.
- **JSON Logging**: All logs are output in JSON format, making them compatible with observability tools like Datadog.

---

## How to Run

Before running the commands, save the OpenAI API key in the `docker-compose.yml` file in `OPENAI_API_KEY`

1. **Build and start the app and database:**
   ```sh
   docker compose up --build -d
   ```
   This command builds the Docker images and starts both the FastAPI app and the Postgres database. On startup, the app automatically ingests the provided recipes into the database.

2. **Start without loading initial data:**
   ```sh
   LOAD_STARTUP_DATA=false docker compose up --build -d
   ```
   Use this command if you want to start the app with an empty database and load recipes manually via the API.

3. **Recipe Ingestion:**
   - **Automatic:** Recipes from `data.zip` or `data/recipes/` are loaded into the database on startup.
   - **Manual (API):** You can also ingest recipes via the `/api/v1/ingest-recipes` endpoint by uploading `.txt` files. This endpoint is useful for adding new recipes at runtime, supporting dynamic updates and integration with other systems.

---

## Assumptions & Design Choices
- **API Naming:** Endpoints use hyphens (`-`) instead of underscores (`_`) for improved readability and consistency with common RESTful API conventions.
- **Logging:** All logs are in JSON format for easy integration with log aggregation and monitoring services (e.g., Datadog).

---

## API Usage Examples

### 1. Recommend Recipe (Text)
- **Endpoint:** `POST /api/v1/recommend-recipe`
- **Request Body:**
  ```json
  {
    "ingredients": ["chicken", "rice", "broccoli"]
  }
  ```
- **Response:**
  ```json
  {
    "recipe": "# Chicken and Broccoli Rice Bowl\n... (Markdown instructions) ..."
  }
  ```

### 2. Recommend Recipe (Image)
- **Endpoint:** `POST /api/v1/recommend-recipe-from-image`
- **Request:** Multipart form with an image file (JPEG, PNG, WEBP, or GIF)

![image](data/example_food_photos/food1.webp)

- **Response:**
  ```json
  {
    "detected_ingredients": ["avocado", "broccoli", "cucumber" "..."],
    "recipe": "# Avocado \n... (Markdown instructions) ..."
  }
  ```

### 3. Ingest Recipes
- **Endpoint:** `POST /api/v1/ingest-recipes`
- **Request:** Multipart form with one or more `.txt` recipe files with the below expected format

```
Quick Chicken Stir-Fry

Ingredients:

    2 chicken breasts, diced
    1 cup mixed vegetables
    2 tbsp soy sauce
    1 tbsp vegetable oil
    1 clove garlic, minced

Instructions:

    Heat oil in a wok over medium-high heat.
    Add garlic and chicken, cook until chicken is nearly done.
    Add vegetables and stir-fry for 2-3 minutes.
    Pour in soy sauce, cook for another minute.
    Serve hot over rice.
```

- **Response:**
  ```json
  {
    "recipes": [
      { "success": true, "recipe": { ... }, "error": null },
      { "success": false, "recipe": null, "error": "Failed to ingest recipe" }
    ]
  }
  ```

---

## Testing
To ensure a clean environment and proper test flow, run each command below one after the other:

1. Reset and start all services:

```bash
docker compose down -v
```
```bash
LOAD_STARTUP_DATA=false docker compose up --build -d
```

2. Run Ingestion

```bash
docker compose exec app pytest tests/e2e/test_ingestion.py
```

3. Run Recommendation

```bash
docker compose exec app pytest tests/e2e/test_recommendation.py
```

---

## Further Improvements
*This section will be filled in later with ideas for future enhancements.*