from fastapi import FastAPI


class API:
    """
    Client initializes and configures the FastAPI application.
    """

    def __init__(self, lifespan):
        """
        Initialize the FastAPI application with OpenAPI metadata.
        Optionally, CORS middleware can be added to the app, if needed.

        Args:
            lifespan: Lifespan context manager for the FastAPI app.
        """
        self.app = FastAPI(
            title="AI Recipe Generator",
            description="Hi, I'm a recipe generator that can help you find recipes based on the ingredients you have.",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json",
            lifespan=lifespan,
        )
