from pydantic import BaseModel, Field


class RecommendRecipeRequest(BaseModel):
    """
    Request schema for recommending a recipe.

    Args:
        ingredients (list[str]): The ingredients to recommend a recipe for.
    """
    ingredients: list[str] = Field(..., description="The ingredients to recommend a recipe for.")


class RecommendRecipeResponse(BaseModel):
    """
    Response schema for recommending a recipe.

    Args:
        recipe (str): The recommended recipe.
    """
    recipe: str = Field(..., description="The recommended recipe.")


class RecipeResponse(BaseModel):
    """
    Response schema for a recipe.

    Args:
        id (int): The ID of the recipe.
        title (str): The title of the recipe.
        ingredients (str): The ingredients of the recipe.
        instructions (str): The instructions of the recipe.
        embedding (list[float] | None): The embedding of the recipe.
        created_at (str | None): The creation date of the recipe.
        updated_at (str | None): The last update date of the recipe.
    """
    id: int
    title: str
    ingredients: str
    instructions: str
    embedding: list[float] | None = None
    created_at: str | None = None
    updated_at: str | None = None


class IngestRecipeResponse(BaseModel):
    """
    Response schema for ingesting a recipe.

    Args:
        success (bool): Whether the recipe was ingested successfully.
        recipe (RecipeResponse | None): The ingested recipe.
        error (str | None): The error message if the recipe was not ingested successfully.
    """
    success: bool = Field(..., description="Whether the recipe was ingested successfully.")
    recipe: RecipeResponse | None = Field(None, description="The ingested recipe.")
    error: str | None = Field(None, description="The error message if the recipe was not ingested successfully.")


class IngestRecipesResponse(BaseModel):
    """
    Response schema for ingesting multiple recipes.

    Args:
        recipes (list[IngestRecipeResponse]): The ingested recipes.
    """
    recipes: list[IngestRecipeResponse] = Field(..., description="The ingested recipes.")


class RecommendRecipeFromImageResponse(BaseModel):
    """
    Response schema for recommending a recipe from an image.

    Args:
        detected_ingredients (list[str]): The ingredients detected in the image.
        recipe (str): The recommended recipe based on detected ingredients.
    """
    detected_ingredients: list[str] = Field(..., description="The ingredients detected in the image.")
    recipe: str = Field(..., description="The recommended recipe based on detected ingredients.")
