"""
Database session management decorators.

This module provides decorators for handling database sessions, including
automatic session cleanup and error handling for repository operations.
"""

from sqlalchemy.exc import IntegrityError


def handle_session(f):
    """
    Decorator to handle the database session.
    """

    def wrapper(self, *args, **kwargs):
        session = self.db_manager.Session()

        try:
            result = f(self, session, *args, **kwargs)
            return result

        except IntegrityError as e:
            session.rollback()
            self.logger.error(f"Error: {e}")
            raise Exception(f"Error: {e}")

        finally:
            session.expunge_all()
            session.close()

    return wrapper
