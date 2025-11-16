"""
Logger utility module.

This module provides a reusable LoggerUtil class to create and manage:
-- Colored console logging
-- File logging with rotation
-- Different log levels
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional

# Import configurations
from config import LOG_DIR


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to console output"""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\x1b[38;2;0;0;135m",
        "INFO": "\x1b[38;2;95;135;255m",
        "WARNING": "\x1b[38;2;215;95;0m",
        "ERROR": "\x1b[38;2;215;0;0m",
        "CRITICAL": "\x1b[38;2;95;0;255m",
    }
    RESET = "\x1b[0m"

    def format(self, record):
        # Add color to the level name
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
            )
        return super().format(record)


class LoggerUtil:
    """
    Utility class for managing loggers across the application

    Usage:
        from utils.logger_util import get_logger
        logger = get_logger(__name__)
        logger.info("This is an info message")
        logger.error("This is an error message")
    """

    _loggers = {}
    _initialized = False
    _log_dir = Path(LOG_DIR)
    _console_level = logging.INFO
    _file_level = logging.DEBUG
    _max_file_size = 5 * 1024 * 1024  # 5 MB
    _backup_count = 5

    _log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    _date_format = "%Y-%m-%d %H:%M:%S"

    @classmethod
    def initialize(
        cls,
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        max_file_size: int = 5 * 1024 * 1024,
        backup_count: int = 5,
    ):
        """Initialize the logging system with custom settings"""
        if cls._initialized:
            return

        cls._console_level = console_level
        cls._file_level = file_level
        cls._max_file_size = max_file_size
        cls._backup_count = backup_count
        cls._initialized = True

    @classmethod
    def get_logger(
        cls,
        name: str,
        console_level: Optional[int] = None,
        file_level: Optional[int] = None,
        max_file_size: Optional[int] = None,
        backup_count: Optional[int] = None,
    ) -> logging.Logger:
        """Get or create a logger with the specified name"""

        # Initialize if not done already
        if not cls._initialized:
            cls.initialize(
                console_level=console_level,
                file_level=file_level,
                max_file_size=max_file_size,
                backup_count=backup_count,
            )

        # Return existing logger if already created
        if name in cls._loggers:
            return cls._loggers[name]

        # Create new logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)  # Capture all levels, handlers will filter

        # Prevent duplicate logs
        if logger.handlers:
            return logger

        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(console_level or cls._console_level)

        ch_formatter = ColoredFormatter(fmt=cls._log_format, datefmt=cls._date_format)
        ch.setFormatter(ch_formatter)
        logger.addHandler(ch)

        # File handler with rotation
        cls._log_dir.mkdir(parents=True, exist_ok=True)
        log_file = cls._log_dir / f"{name.replace('.', '_')}.log"
        fh = RotatingFileHandler(
            log_file,
            maxBytes=cls._max_file_size,
            backupCount=cls._backup_count,
            encoding="utf-8",
        )
        fh.setLevel(file_level or cls._file_level)
        fh_formatter = logging.Formatter(cls._log_format, datefmt=cls._date_format)
        fh.setFormatter(fh_formatter)
        logger.addHandler(fh)

        # Store logger
        cls._loggers[name] = logger

        return logger

    @classmethod
    def set_level(cls, level: int):
        """Set the logging level for all loggers"""
        cls._console_level = level
        for logger in cls._loggers.values():
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler) and not isinstance(
                    handler, RotatingFileHandler
                ):
                    handler.setLevel(level)

    @classmethod
    def disable_console_logging(cls):
        """Disable console logging for all loggers"""
        for logger in cls._loggers.values():
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler) and not isinstance(
                    handler, RotatingFileHandler
                ):
                    handler.setLevel(logging.CRITICAL + 1)

    @classmethod
    def enable_console_logging(cls, level: Optional[int]):
        """Enable console logging for all loggers"""
        target_level = level or cls._console_level
        for logger in logger.handlers:
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler) and not isinstance(
                    handler, RotatingFileHandler
                ):
                    handler.setLevel(target_level)


# Instance method to get logger
def get_logger(
    name: str,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    max_file_size: int = 5 * 1024 * 1024,
    backup_count: int = 5,
):
    return LoggerUtil.get_logger(
        name=name,
        console_level=console_level,
        file_level=file_level,
        max_file_size=max_file_size,
        backup_count=backup_count,
    )


# [Optional] Configure logging at module import (can be customized in main.py)
def configure_logging(
    console_level: int = logging.INFO, file_level: int = logging.DEBUG
):
    """Configure the logging system with custom settings"""
    LoggerUtil.initialize(console_level=console_level, file_level=file_level)
