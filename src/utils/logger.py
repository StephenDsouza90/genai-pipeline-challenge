"""
Application logging configuration and utilities.

This module provides a centralized logging system using JSON formatting
for structured logging, suitable for production environments and log
aggregation systems.
"""

import logging

import json_log_formatter

from src.constants import APP_LOGGER_NAME


class Logger:
    """
    Logger configures and provides a singleton JSON-formatted logger for the application.

    This logger outputs logs in JSON format, suitable for structured logging and integration with log management systems.
    """

    _logger = None

    def __init__(self):
        """
        Logger
        -------------
        Initialize the Logger and set up JSON logging if not already configured.
        """
        if self._logger is None:
            self.setup_logging()

    @classmethod
    def setup_logging(cls):
        """
        Setup Logging
        -------------
        Set up a JSON log formatter and attach it to the logger instance.
        """
        if cls._logger is None:
            json_handler = logging.StreamHandler()
            json_handler.setFormatter(json_log_formatter.JSONFormatter())

            cls._logger = logging.getLogger(APP_LOGGER_NAME)
            cls._logger.addHandler(json_handler)
            cls._logger.setLevel(logging.INFO)
            cls._logger.propagate = False

    @classmethod
    def get_logger(cls):
        """
        Get Logger
        -------------
        Retrieve the singleton logger instance for use throughout the application.
        """
        return cls._logger
