"""Structured logging configuration for Mutual Fund FAQ Assistant."""

import logging
import sys
from typing import Optional


class SafeFormatter(logging.Formatter):
    """Custom formatter ensuring standardized log output format."""

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        super().__init__(
            fmt=fmt or "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt=datefmt or "%Y-%m-%d %H:%M:%S",
        )


def setup_logging(log_level: str = "INFO") -> None:
    """Initialize root logging configuration."""
    level = getattr(logging, log_level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to prevent duplicate log lines
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(SafeFormatter())

    root_logger.addHandler(console_handler)

    # Suppress verbose third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance."""
    return logging.getLogger(name)
