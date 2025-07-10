"""
Database connection and session management.

This module provides database connectivity, session management, and initialization
functionality for the PostgreSQL database with pgvector extension support.
"""

import time

from sqlalchemy import create_engine, text, Connection, Engine
from sqlalchemy.orm import sessionmaker

from src.data.base import Base
from src.config import Settings
from src.constants import VECTOR_EXTENSION_QUERY
from src.utils.logger import Logger


class DatabaseManager:
    """
    Manages database connections and sessions.
    """

    def __init__(self, settings: Settings, logger: Logger):
        """
        Initialize database manager with connection URL.

        Args:
            settings: Settings object containing database configuration.
            logger: Logger object for logging.
        """
        self.settings = settings
        self.logger = logger
        self.engine: Engine | None = None
        self.Session = sessionmaker(autoflush=True)
        self._setup_engine()

    def _setup_engine(self) -> None:
        """
        Initialize database engine and session factory.
        """
        if self.engine:
            return

        self.engine = create_engine(
            self.settings.database_url,
            echo=True,
            pool_pre_ping=True,
            pool_recycle=self.settings.database_pool_recycle,
        )

        self.Session.configure(bind=self.engine)

    def bootstrap(
        self,
        max_retries: int | None = None,
        retry_delay: int | None = None,
    ):
        """
        Connect to the database and create the tables.

        Args:
            max_retries: The maximum number of retries to connect to the database.
            retry_delay: The delay between retries in seconds.

        Raises:
            Exception: If the database connection fails.
        """
        connection: Connection | None = None

        max_retries = max_retries or self.settings.database_max_retries
        retry_delay = retry_delay or self.settings.database_retry_delay

        for i in range(max_retries):
            try:
                connection = self.engine.connect()
                self._enable_pg_vector(connection)
                break

            except Exception as e:
                self.logger.error(
                    f"Failed to connect to the database after {i + 1} attempts: {e}"
                )
                if i < max_retries - 1:
                    time.sleep(retry_delay)

        if not connection:
            message = f"Failed to connect to the database after {max_retries} attempts"
            self.logger.error(message)
            raise Exception(message)

        self._create_tables()
        connection.close()

    def _enable_pg_vector(self, connection: Connection):
        connection.execute(text(VECTOR_EXTENSION_QUERY))
        connection.commit()

    def _create_tables(self):
        """
        Create all database tables.
        """
        Base.metadata.create_all(bind=self.engine)

    def close(self):
        """
        Close database connections.
        """
        if self.engine:
            self.engine.dispose()
            self.engine = None
