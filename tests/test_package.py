# tests/test_package.py
import tomllib
from pathlib import Path

import jc_selenium_helper

PYPROJECT = Path(__file__).parent.parent / "pyproject.toml"


def test_version_is_exposed():
    assert isinstance(jc_selenium_helper.__version__, str)


def test_version_matches_pyproject():
    version = tomllib.loads(PYPROJECT.read_text())["project"]["version"]
    assert jc_selenium_helper.__version__ == version
