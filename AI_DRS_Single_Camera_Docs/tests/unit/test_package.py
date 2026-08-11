"""
Unit tests for package initialization and versioning
"""
import ai_drs

def test_package_version():
    assert hasattr(ai_drs, "__version__")
    assert isinstance(ai_drs.__version__, str)
    assert ai_drs.__version__ == "0.1.0"
