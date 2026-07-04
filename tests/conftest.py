# tests/conftest.py
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from jc_selenium_helper.browser import Browser

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1280, 1024)
    yield driver
    driver.quit()


@pytest.fixture
def fixture_url():
    def _url(name: str) -> str:
        path = FIXTURES / name
        assert path.exists(), f"fixture not found: {path}"
        return path.as_uri()

    return _url


@pytest.fixture
def browser(driver):
    return Browser(driver, default_timeout=10, poll_pause=0.2)
