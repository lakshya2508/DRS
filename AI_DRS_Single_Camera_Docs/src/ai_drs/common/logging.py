"""
Logging infrastructure for AI DRS
"""
import logging
import sys
import os

def setup_logger(name: str = "ai_drs", level: str = None) -> logging.Logger:
    """Configures and returns a structured logger for the application."""
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO").upper()

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
