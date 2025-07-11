"""
Error mapping for the API.

This module defines functions to map exceptions to HTTPExceptions with appropriate status codes and detail messages.
"""

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from src.utils.logger import Logger


def map_service_exception(exc: Exception, logger: Logger) -> HTTPException:
    """
    This function takes an exception as input and maps it to an appropriate HTTPException with a specific status code and detail message.

    Args:
        exc (Exception): The exception to be mapped.
        logger (Logger): The logger to use for logging.

    Returns:
        HTTPException: The mapped HTTPException with a status code and detail message.
    """
    if isinstance(exc, IntegrityError):
        logger.error(f"Integrity error: {str(exc)}")
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integrity error: {str(exc)}",
        )

    if isinstance(exc, UnicodeDecodeError):
        logger.error(f"File encoding error: {str(exc)}")
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file encoding. Please ensure the file is UTF-8 encoded.",
        )

    if isinstance(exc, ValueError):
        error_msg = str(exc)
        logger.error(f"Validation error: {error_msg}")

        # Handle specific validation cases
        if "Ingredients cannot be empty" in error_msg:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ingredients cannot be empty",
            )
        elif "Invalid file type" in error_msg:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Please upload an image file.",
            )
        elif "Invalid image format" in error_msg:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
        elif "No ingredients could be detected" in error_msg:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
        elif "not enough values to unpack" in error_msg:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Please upload an image file.",
            )
        else:
            # Generic validation error
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )

    logger.error(f"Unexpected error: {str(exc)}")
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred while processing your request. Please try again later.",
    )
