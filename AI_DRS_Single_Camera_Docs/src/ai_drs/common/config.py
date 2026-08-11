"""
Configuration management loader for AI DRS
"""
import os
from pathlib import Path
from typing import Any, Dict
import yaml

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.config")

def get_project_root() -> Path:
    """Returns the absolute root directory of the project."""
    return Path(__file__).resolve().parent.parent.parent.parent

def load_yaml_config(relative_path: str) -> Dict[str, Any]:
    """Loads a YAML configuration file from the configs directory or absolute path."""
    root = get_project_root()
    full_path = root / relative_path if not os.path.isabs(relative_path) else Path(relative_path)

    if not full_path.exists():
        logger.warning(f"Configuration file not found: {full_path}")
        return {}

    with open(full_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    logger.debug(f"Loaded config from {full_path}")
    return config
