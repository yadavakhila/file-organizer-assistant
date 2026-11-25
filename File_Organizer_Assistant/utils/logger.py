"""Centralized logging setup for File Organizer Assistant."""

import logging
from pathlib import Path
from typing import Optional

from config.settings import APP_LOG_PATH


def get_logger(name: str = "file_organizer", log_path: Optional[Path] = None) -> logging.Logger:
    """Return a configured logger writing to both file and rotating-safe stream."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    target_path = log_path or APP_LOG_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    try:
        file_handler = logging.FileHandler(target_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError:
        # Fall back to null/console if log file cannot be opened
        pass

    return logger
