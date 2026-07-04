# tests/test_package.py
import jc_selenium_helper


def test_version_is_exposed():
    assert isinstance(jc_selenium_helper.__version__, str)
    assert jc_selenium_helper.__version__ == "0.1.0"
