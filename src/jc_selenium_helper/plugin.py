"""pytest plugin exposing ready-made fixtures.

Enabled automatically when the package is installed with the ``pytest`` extra
(registered via the ``pytest11`` entry point). Fixtures are namespaced with a
``jc_`` prefix to avoid clashing with a project's own ``browser`` fixture.
"""

from __future__ import annotations

import pytest

from jc_selenium_helper.browser import Browser


@pytest.fixture
def jc_chrome_options():
    """Sensible default Chrome options; override in a project conftest to customize."""
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return options


@pytest.fixture
def jc_browser(selenium) -> Browser:
    """Wrap the pytest-selenium ``selenium`` driver in a :class:`Browser`."""
    return Browser(selenium)
