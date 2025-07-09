import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    """
    
    # Database configuration
    database_url: str = os.getenv("DB_URL")
    
    # OpenAI configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    openai_chat_model: str = os.getenv("OPENAI_MODEL")
    openai_embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL")
    
    # # Application configuration
    # app_name: str = "What's for Dinner"
    # debug: bool = False
    
    # class Config:
    #     env_file = ".env"
    #     env_file_encoding = "utf-8"
