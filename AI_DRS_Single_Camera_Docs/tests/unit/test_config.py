"""
Unit tests for configuration loader
"""
from ai_drs.common.config import get_project_root, load_yaml_config

def test_project_root():
    root = get_project_root()
    assert root.exists()
    assert (root / "pyproject.toml").exists()

def test_load_camera_config():
    config = load_yaml_config("configs/camera.yaml")
    assert "camera" in config
    assert config["camera"]["fps"] == 60
    assert config["pitch_geometry"]["length_meters"] == 20.12

def test_load_decision_config():
    config = load_yaml_config("configs/decision.yaml")
    assert "thresholds" in config
    assert config["thresholds"]["minimum_track_confidence"] == 0.70

def test_load_missing_config():
    config = load_yaml_config("configs/non_existent.yaml")
    assert config == {}
