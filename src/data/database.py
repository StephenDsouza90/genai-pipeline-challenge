import time

from sqlalchemy import create_engine, text, Connection, Engine
from sqlalchemy.orm import sessionmaker

from src.data.base import Base
from src.config import Settings
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
        """
        self.database_url = settings.database_url
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
            self.database_url,
            echo=True,
            pool_pre_ping=True,
            pool_recycle=300,
        )

        self.Session.configure(bind=self.engine)

    def bootstrap(
        self,
        max_retries: int = 5,
        retry_delay: int = 2,
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

        for i in range(max_retries):
            try:
                connection = self.engine.connect()
                self._enable_pg_vector(connection)
                break

            except Exception as e:
                self.logger.error(f"Failed to connect to the database after {i + 1} attempts: {e}")
                if i < max_retries - 1:
                    time.sleep(retry_delay)

        if not connection:
            message = f"Failed to connect to the database after {max_retries} attempts"
            self.logger.error(message)
            raise Exception(message)

        self._create_tables()
        connection.close()

    def _enable_pg_vector(self, connection: Connection):
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
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
