"""
Unit tests for logging infrastructure
"""
import logging
from ai_drs.common.logging import setup_logger

def test_setup_logger():
    logger = setup_logger("test_logger", level="DEBUG")
    assert logger.name == "test_logger"
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) >= 1
