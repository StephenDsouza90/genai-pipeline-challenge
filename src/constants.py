"""
Application constants that are not configurable settings.
"""

# Image Processing
IMAGE_CONTENT_TYPE_PREFIX = "image/"
IMAGE_BASE64_PREFIX = "data:image/jpeg;base64,"

# Recipe Processing
RECIPE_SECTIONS = {
    "INGREDIENTS": "ingredients:",
    "INSTRUCTIONS": "instructions:",
}

# File Processing
BULLET_POINT_CHARS = "•-*1234567890. "
MINIMUM_INGREDIENT_LENGTH = 1

# Database
VECTOR_EXTENSION_NAME = "vector"
VECTOR_EXTENSION_QUERY = "CREATE EXTENSION IF NOT EXISTS vector"

# Logging
APP_LOGGER_NAME = "app_logger"
