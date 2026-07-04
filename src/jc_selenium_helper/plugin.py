"""pytest plugin exposing ready-made fixtures.

Enabled automatically when the package is installed with the ``pytest`` extra
(registered via the ``pytest11`` entry point). Fixtures are namespaced with a
``jc_`` prefix to avoid clashing with a project's own ``browser`` fixture.
"""

from __future__ import annotations

import os
import warnings

import pytest

from jc_selenium_helper.browser import Browser

#: Chrome flags that weaken the browser's security posture. Off by default;
#: opt in via the ``jc_insecure_chrome`` fixture or the ``JC_SELENIUM_INSECURE``
#: environment variable (see :func:`jc_chrome_options`).
INSECURE_CHROME_ARGS = ("--no-sandbox", "--ignore-certificate-errors")

_ENV_INSECURE = "JC_SELENIUM_INSECURE"
_TRUTHY = frozenset({"1", "true", "yes", "on"})


class InsecureChromeOptionsWarning(UserWarning):
    """Emitted when the insecure Chrome flags are enabled."""


def _env_opt_in() -> bool:
    return os.environ.get(_ENV_INSECURE, "").strip().lower() in _TRUTHY


@pytest.fixture
def jc_insecure_chrome() -> bool:
    """Opt in to insecure Chrome flags (``--no-sandbox``, ``--ignore-certificate-errors``).

    Defaults to ``False``. Override in a project ``conftest.py`` to return ``True``,
    or set the ``JC_SELENIUM_INSECURE`` environment variable — either enables the
    flags in :func:`jc_chrome_options` and triggers an
    :class:`InsecureChromeOptionsWarning`.
    """
    return False


@pytest.fixture
def jc_chrome_options(jc_insecure_chrome):
    """Sensible default headless Chrome options; override in a project conftest to customize.

    The security-weakening flags in :data:`INSECURE_CHROME_ARGS` are **off by
    default**. Enable them (e.g. for sandboxed CI containers) by overriding the
    ``jc_insecure_chrome`` fixture to return ``True`` or by setting the
    ``JC_SELENIUM_INSECURE`` environment variable; doing so emits an
    :class:`InsecureChromeOptionsWarning`.
    """
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")

    if jc_insecure_chrome or _env_opt_in():
        warnings.warn(
            "jc-selenium-helper: enabling insecure Chrome flags "
            f"({', '.join(INSECURE_CHROME_ARGS)}). This disables the browser sandbox "
            "and TLS certificate verification. Enabled via the jc_insecure_chrome "
            f"fixture or the {_ENV_INSECURE} environment variable.",
            InsecureChromeOptionsWarning,
            stacklevel=2,
        )
        for arg in INSECURE_CHROME_ARGS:
            options.add_argument(arg)

    return options


@pytest.fixture
def chrome_options(jc_chrome_options):
    """Feed jc_chrome_options into pytest-selenium's driver.

    pytest-selenium builds its Chrome driver from a fixture named
    ``chrome_options``; delegating here makes the package's defaults apply while
    letting users customize by overriding ``jc_chrome_options``.
    """
    return jc_chrome_options


@pytest.fixture
def jc_browser(selenium) -> Browser:
    """Wrap the pytest-selenium ``selenium`` driver in a :class:`Browser`."""
    return Browser(selenium)
