from fastapi import APIRouter


class HealthRoutes:
    """
    This class defines the API routes for the Health Check.
    """

    def __init__(self):
        """
        Initialize the Health Routes class.
        """
        self.router = APIRouter(tags=["health"])
        self.setup_routes()

    def setup_routes(self):
        @self.router.get("/health")
        async def health_check():
            """
            Health check endpoint.
            """
            return {"status": "healthy"}
