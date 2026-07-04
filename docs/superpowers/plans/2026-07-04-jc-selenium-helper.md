# jc-selenium-helper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package a tester's internal Selenium utilities into a documented, PyPI-publishable Python package `jc-selenium-helper` with a clean English API, a legacy compatibility adapter, an optional pytest plugin, config/axe extras, and MkDocs/Read the Docs documentation.

**Architecture:** `src/` layout, single importable package `jc_selenium_helper` with focused modules. Core depends only on `selenium`. A `Browser` class wraps a Selenium `WebDriver` (XPath-default locators, optional `by=`, constructor-configurable timeouts). A `LegacyBrowser` subclass preserves the original German-named API as deprecated aliases so the existing internal test suite keeps working. pytest plugin, Dynaconf config loader, and axe accessibility helper live behind dependency extras. Tests drive local HTML fixtures via headless Chrome.

**Tech Stack:** Python ≥3.12, Selenium 4, pytest + pytest-selenium, Dynaconf, axe-selenium-python, MkDocs (readthedocs theme + awesome-pages), ruff, nox, pre-commit, bump-my-version.

## Global Constraints

- PyPI name `jc-selenium-helper`; import name `jc_selenium_helper`.
- `src/` layout; single package with focused modules.
- Python floor: `>=3.12`; test matrix 3.12–3.14.
- Core install depends on `selenium` only. `dynaconf`, `pytest`/`pytest-selenium`, and `axe-selenium-python` are behind extras `config`, `pytest`, `axe`.
- Do **not** add `colormap` or `easydev` — rgb→hex is implemented in-package.
- License: MIT. Author: Alexander Jacob <alexander.jacob@jacob-consulting.de>.
- Public API is clean English; German/ad-hoc names exist only in `legacy.py` and must emit `DeprecationWarning`.
- Locators default to XPath; every locator-taking method accepts `by=` (a Selenium `By` value).
- Docs are Markdown via MkDocs, mirroring `../django-crud-views`.
- Commit after every task with a conventional-commit message.

---

## File Structure

- `pyproject.toml` — packaging, deps, extras, tool config (ruff, pytest, bump-my-version).
- `src/jc_selenium_helper/__init__.py` — exports `Browser`, `__version__`.
- `src/jc_selenium_helper/colors.py` — `rgb_to_hex()`.
- `src/jc_selenium_helper/browser.py` — clean `Browser` class (finders, waits, actions, assertions, frame).
- `src/jc_selenium_helper/legacy.py` — `LegacyBrowser(Browser)` deprecated aliases + verbatim legacy behavior.
- `src/jc_selenium_helper/plugin.py` — pytest plugin fixtures (entry point `pytest11`).
- `src/jc_selenium_helper/config.py` — `get_settings()` Dynaconf loader.
- `src/jc_selenium_helper/axe.py` — `run_axe()` accessibility helper.
- `src/jc_selenium_helper/py.typed` — PEP 561 marker.
- `tests/conftest.py` — headless Chrome `driver` fixture, `fixture_url` helper.
- `tests/fixtures/basic.html`, `tests/fixtures/frame.html`, `tests/fixtures/target.html` — local pages.
- `tests/test_*.py` — one test module per source module.
- `docs/` + `mkdocs.yml` + `.readthedocs.yaml` — documentation.
- `noxfile.py`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml` — tooling/CI.

---

### Task 1: Project scaffolding & packaging

**Files:**
- Create: `pyproject.toml`
- Create: `src/jc_selenium_helper/__init__.py`
- Create: `src/jc_selenium_helper/py.typed`
- Create: `tests/test_package.py`

**Interfaces:**
- Produces: importable package `jc_selenium_helper` exposing `__version__: str` and (added in Task 3) `Browser`.

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[project]
name = "jc-selenium-helper"
version = "0.1.0"
description = "Selenium WebDriver helper utilities for writing browser tests"
authors = [{ name = "Alexander Jacob", email = "alexander.jacob@jacob-consulting.de" }]
license = { text = "MIT" }
readme = "README.md"
requires-python = ">=3.12"
classifiers = [
    "Intended Audience :: Developers",
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Framework :: Pytest",
    "Topic :: Software Development :: Testing",
]
dependencies = [
    "selenium>=4.38.0",
]

[project.urls]
Homepage = "https://github.com/jacob-consulting/jc-selenium-helper"
Documentation = "https://jc-selenium-helper.readthedocs.io"

[project.optional-dependencies]
pytest = ["pytest>=8", "pytest-selenium>=4.1.0"]
config = ["dynaconf>=3.2"]
axe = ["axe-selenium-python>=2.1.6"]
all = ["jc-selenium-helper[pytest,config,axe]"]
dev = [
    "ruff",
    "pre-commit",
    "bump-my-version",
    "mkdocs>=1.6.1",
    "mkdocs-awesome-pages-plugin>=2.10.1",
]
test = [
    "jc-selenium-helper[pytest,config,axe]",
    "nox",
    "pytest-cov",
    "pytest-xdist",
]

[project.entry-points.pytest11]
jc_selenium_helper = "jc_selenium_helper.plugin"

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
jc_selenium_helper = ["py.typed"]

[tool.ruff]
line-length = 120
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-p no:cacheprovider"
```

Note: the `pytest11` entry point points at `plugin.py`, created in Task 8. Until then the module is absent; that is fine because the extra isn't installed in Task 1. Install with `pip install -e .` (core only) for Tasks 1–7.

- [ ] **Step 2: Write `src/jc_selenium_helper/__init__.py`**

```python
"""Selenium WebDriver helper utilities for writing browser tests."""

__version__ = "0.1.0"

__all__ = ["__version__"]
```

- [ ] **Step 3: Create the PEP 561 marker**

Create empty file `src/jc_selenium_helper/py.typed` (0 bytes).

- [ ] **Step 4: Write the smoke test**

```python
# tests/test_package.py
import jc_selenium_helper


def test_version_is_exposed():
    assert isinstance(jc_selenium_helper.__version__, str)
    assert jc_selenium_helper.__version__ == "0.1.0"
```

- [ ] **Step 5: Install and run the test**

Run:
```bash
pip install -e .
pytest tests/test_package.py -v
```
Expected: PASS (1 passed).

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml src/jc_selenium_helper/__init__.py src/jc_selenium_helper/py.typed tests/test_package.py
git commit -m "chore: scaffold jc-selenium-helper package"
```

---

### Task 2: `colors.rgb_to_hex`

**Files:**
- Create: `src/jc_selenium_helper/colors.py`
- Test: `tests/test_colors.py`

**Interfaces:**
- Produces: `rgb_to_hex(rgb_string: str) -> str` — parses a CSS `rgb(...)`/`rgba(...)` string to `#rrggbb`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_colors.py
import pytest

from jc_selenium_helper.colors import rgb_to_hex


@pytest.mark.parametrize(
    "value, expected",
    [
        ("rgb(255, 0, 0)", "#ff0000"),
        ("rgb(0, 128, 0)", "#008000"),
        ("rgba(16, 32, 48, 0.5)", "#102030"),
        ("rgb(0,0,0)", "#000000"),
    ],
)
def test_rgb_to_hex(value, expected):
    assert rgb_to_hex(value) == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_colors.py -v`
Expected: FAIL (ModuleNotFoundError: jc_selenium_helper.colors).

- [ ] **Step 3: Write the implementation**

```python
# src/jc_selenium_helper/colors.py
"""Color conversion helpers (replaces the colormap/easydev dependency)."""

from __future__ import annotations


def rgb_to_hex(rgb_string: str) -> str:
    """Convert a CSS ``rgb(...)`` or ``rgba(...)`` string to ``#rrggbb``.

    The alpha channel of ``rgba`` is ignored.
    """
    inner = rgb_string[rgb_string.index("(") + 1 : rgb_string.index(")")]
    parts = [int(float(component.strip())) for component in inner.split(",")[:3]]
    r, g, b = parts
    return f"#{r:02x}{g:02x}{b:02x}"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_colors.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add src/jc_selenium_helper/colors.py tests/test_colors.py
git commit -m "feat: add rgb_to_hex color helper"
```

---

### Task 3: Test harness + `Browser` finders

Establishes the headless-Chrome test infrastructure used by all later Browser tasks, plus the `Browser` skeleton and finder methods.

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/fixtures/basic.html`
- Create: `src/jc_selenium_helper/browser.py`
- Modify: `src/jc_selenium_helper/__init__.py`
- Test: `tests/test_browser_finders.py`

**Interfaces:**
- Produces:
  - `Browser(driver, default_timeout: float = 120, poll_pause: float = 1)`
  - `Browser.open(url: str) -> None`
  - `Browser.find(locator: str, by: str = By.XPATH) -> WebElement`
  - `Browser.find_all(locator: str, by: str = By.XPATH) -> list[WebElement]`
  - `Browser.exists(locator: str, by: str = By.XPATH) -> bool`
  - conftest fixtures: `driver` (session-scoped headless Chrome), `fixture_url(name: str) -> str`, `browser` (function-scoped `Browser` around `driver`).
- Consumes: nothing from earlier tasks.

- [ ] **Step 1: Write the test conftest**

```python
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
```

- [ ] **Step 2: Write the HTML fixture**

```html
<!-- tests/fixtures/basic.html -->
<!doctype html>
<html>
  <head><title>basic</title></head>
  <body>
    <h1 id="title">Hello</h1>
    <ul>
      <li class="item">a</li>
      <li class="item">b</li>
      <li class="item">c</li>
    </ul>
    <button id="btn">Click</button>
  </body>
</html>
```

- [ ] **Step 3: Write the failing finder tests**

```python
# tests/test_browser_finders.py
from selenium.webdriver.common.by import By


def test_find_returns_element(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    assert browser.find("//h1[@id='title']").text == "Hello"


def test_find_with_css(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    assert browser.find("#title", by=By.CSS_SELECTOR).text == "Hello"


def test_find_all_returns_list(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    items = browser.find_all("//li[@class='item']")
    assert [e.text for e in items] == ["a", "b", "c"]


def test_exists_true_and_false(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    assert browser.exists("//h1[@id='title']") is True
    assert browser.exists("//h1[@id='missing']") is False
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `pytest tests/test_browser_finders.py -v`
Expected: FAIL (ModuleNotFoundError: jc_selenium_helper.browser).

- [ ] **Step 5: Write the `Browser` skeleton + finders**

```python
# src/jc_selenium_helper/browser.py
"""A thin, ergonomic wrapper around a Selenium WebDriver."""

from __future__ import annotations

import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait


class Browser:
    """Wraps a Selenium ``WebDriver`` with convenience helpers.

    Locators default to XPath; pass ``by=By.CSS_SELECTOR`` (or any Selenium
    ``By`` value) to use a different strategy.
    """

    def __init__(self, driver, default_timeout: float = 120, poll_pause: float = 1) -> None:
        self.driver = driver
        self.default_timeout = default_timeout
        self.poll_pause = poll_pause

    # -- navigation --
    def open(self, url: str) -> None:
        self.driver.get(url)

    # -- finders --
    def find(self, locator: str, by: str = By.XPATH) -> WebElement:
        return self.driver.find_element(by, locator)

    def find_all(self, locator: str, by: str = By.XPATH) -> list[WebElement]:
        return self.driver.find_elements(by, locator)

    def exists(self, locator: str, by: str = By.XPATH) -> bool:
        try:
            self.driver.find_element(by, locator)
        except NoSuchElementException:
            return False
        return True
```

- [ ] **Step 6: Export `Browser` from the package**

Replace `src/jc_selenium_helper/__init__.py` with:

```python
"""Selenium WebDriver helper utilities for writing browser tests."""

from jc_selenium_helper.browser import Browser

__version__ = "0.1.0"

__all__ = ["Browser", "__version__"]
```

- [ ] **Step 7: Run the finder tests**

Run: `pytest tests/test_browser_finders.py tests/test_package.py -v`
Expected: PASS (5 passed). Requires Chrome + a matching chromedriver on PATH.

- [ ] **Step 8: Commit**

```bash
git add tests/conftest.py tests/fixtures/basic.html src/jc_selenium_helper/browser.py src/jc_selenium_helper/__init__.py tests/test_browser_finders.py
git commit -m "feat: add Browser finders and headless-chrome test harness"
```

---

### Task 4: `Browser` waits

**Files:**
- Modify: `src/jc_selenium_helper/browser.py`
- Modify: `tests/fixtures/basic.html` (add a delayed element)
- Test: `tests/test_browser_waits.py`

**Interfaces:**
- Consumes: `Browser` from Task 3.
- Produces:
  - `wait_present(locator, by=By.XPATH, timeout=None) -> WebElement`
  - `wait_clickable(locator, by=By.XPATH, timeout=None) -> WebElement`
  - `wait_not_present(locator, by=By.XPATH, timeout=None) -> bool`
  - `wait_document_ready(timeout=None) -> None`
  - `wait_page_loaded(check_path, by=By.XPATH, retries=5, interval=10) -> None`
  - (`timeout=None` means "use `self.default_timeout`".)

- [ ] **Step 1: Add a delayed element to the fixture**

Append inside `<body>` of `tests/fixtures/basic.html`, before `</body>`:

```html
    <div id="delayed"></div>
    <script>
      setTimeout(function () {
        document.getElementById("delayed").innerHTML =
          '<span id="late">here</span>';
      }, 500);
    </script>
```

- [ ] **Step 2: Write the failing wait tests**

```python
# tests/test_browser_waits.py
import pytest
from selenium.common.exceptions import TimeoutException


def test_wait_present_returns_element(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    assert browser.wait_present("//span[@id='late']").text == "here"


def test_wait_present_times_out(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    with pytest.raises(TimeoutException):
        browser.wait_present("//span[@id='never']", timeout=1)


def test_wait_clickable_returns_element(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    assert browser.wait_clickable("//button[@id='btn']").tag_name == "button"


def test_wait_document_ready(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.wait_document_ready()  # should not raise


def test_wait_page_loaded_on_present_element(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.wait_page_loaded("//h1[@id='title']", retries=1, interval=1)
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `pytest tests/test_browser_waits.py -v`
Expected: FAIL (AttributeError: 'Browser' object has no attribute 'wait_present').

- [ ] **Step 4: Add the wait methods to `Browser`**

Insert after the finders block in `src/jc_selenium_helper/browser.py`:

```python
    # -- waits --
    def _timeout(self, timeout: float | None) -> float:
        return self.default_timeout if timeout is None else timeout

    def wait_present(self, locator: str, by: str = By.XPATH, timeout: float | None = None) -> WebElement:
        WebDriverWait(self.driver, self._timeout(timeout)).until(
            EC.presence_of_element_located((by, locator))
        )
        return self.driver.find_element(by, locator)

    def wait_clickable(self, locator: str, by: str = By.XPATH, timeout: float | None = None) -> WebElement:
        WebDriverWait(self.driver, self._timeout(timeout)).until(
            EC.element_to_be_clickable((by, locator))
        )
        return self.driver.find_element(by, locator)

    def wait_not_present(self, locator: str, by: str = By.XPATH, timeout: float | None = None) -> bool:
        seconds = self._timeout(timeout)
        try:
            WebDriverWait(self.driver, seconds).until(
                EC.invisibility_of_element_located((by, locator))
            )
        except TimeoutException as exc:
            raise TimeoutException(
                f"Element '{locator}' still present after {seconds}s"
            ) from exc
        return True

    def wait_document_ready(self, timeout: float | None = None) -> None:
        seconds = self._timeout(timeout)
        elapsed = 0.0
        while self.driver.execute_script("return document.readyState") != "complete":
            time.sleep(self.poll_pause)
            elapsed += self.poll_pause
            if elapsed > seconds:
                raise TimeoutError("document.readyState never reached 'complete'")

    def wait_page_loaded(
        self,
        check_path: str,
        by: str = By.XPATH,
        retries: int = 5,
        interval: float = 10,
    ) -> None:
        """Wait for ``check_path`` to appear, refreshing between attempts.

        Generic replacement for the app-specific ``seite_geladen`` loop.
        """
        time.sleep(self.poll_pause)
        attempt = 0
        while not self.driver.find_elements(by, check_path):
            self.driver.refresh()
            time.sleep(interval)
            attempt += 1
            if attempt > retries:
                raise TimeoutError(f"Page not loaded (missing {check_path})")
        self.wait_document_ready()
```

- [ ] **Step 5: Run the wait tests**

Run: `pytest tests/test_browser_waits.py -v`
Expected: PASS (5 passed).

- [ ] **Step 6: Commit**

```bash
git add src/jc_selenium_helper/browser.py tests/fixtures/basic.html tests/test_browser_waits.py
git commit -m "feat: add Browser wait helpers"
```

---

### Task 5: `Browser` actions

**Files:**
- Modify: `src/jc_selenium_helper/browser.py`
- Modify: `tests/fixtures/basic.html` (add interactive elements)
- Create: `tests/fixtures/target.html`
- Test: `tests/test_browser_actions.py`

**Interfaces:**
- Consumes: `Browser` finders/waits from Tasks 3–4.
- Produces:
  - `wait_and_click(locator, by=By.XPATH, timeout=None) -> None`
  - `double_click(locator, by=By.XPATH, pause=0) -> None`
  - `hover(locator, by=By.XPATH) -> None`
  - `hover_with_offset(locator, x_offset, y_offset, by=By.XPATH) -> None`
  - `move_to(locator, by=By.XPATH) -> None`
  - `wait_move_click(locator, by=By.XPATH, timeout=None) -> None`
  - `type_text(locator, text, by=By.XPATH) -> None`
  - `upload_file(css_selector, path) -> None`
  - `click_in_new_tab(locator, check_path, by=By.XPATH, check_by=By.XPATH) -> None`

- [ ] **Step 1: Add interactive elements to the fixture**

Insert inside `<body>` of `tests/fixtures/basic.html`, before the `<div id="delayed">` line:

```html
    <input id="text-input" type="text" />
    <button id="dbl" ondblclick="this.textContent='double'">plain</button>
    <button id="clickable" onclick="this.textContent='clicked'">go</button>
    <a id="newtab" href="target.html" target="_blank">open</a>
```

- [ ] **Step 2: Create the new-tab target fixture**

```html
<!-- tests/fixtures/target.html -->
<!doctype html>
<html>
  <head><title>target</title></head>
  <body><p id="target">target page</p></body>
</html>
```

- [ ] **Step 3: Write the failing action tests**

```python
# tests/test_browser_actions.py
def test_type_text(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.type_text("//input[@id='text-input']", "hello")
    assert browser.find("//input[@id='text-input']").get_attribute("value") == "hello"


def test_wait_and_click(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.wait_and_click("//button[@id='clickable']")
    assert browser.find("//button[@id='clickable']").text == "clicked"


def test_double_click(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.double_click("//button[@id='dbl']")
    assert browser.find("//button[@id='dbl']").text == "double"


def test_hover_does_not_raise(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.hover("//button[@id='clickable']")


def test_move_to_does_not_raise(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.move_to("//button[@id='clickable']")


def test_click_in_new_tab_returns_to_main(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.click_in_new_tab("//a[@id='newtab']", "//p[@id='target']")
    assert len(browser.driver.window_handles) == 1
    assert browser.find("//h1[@id='title']").text == "Hello"
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `pytest tests/test_browser_actions.py -v`
Expected: FAIL (AttributeError: no attribute 'type_text').

- [ ] **Step 5: Add the action methods to `Browser`**

Insert after the waits block in `src/jc_selenium_helper/browser.py`:

```python
    # -- actions --
    def wait_and_click(self, locator: str, by: str = By.XPATH, timeout: float | None = None) -> None:
        self.wait_clickable(locator, by, timeout).click()

    def double_click(self, locator: str, by: str = By.XPATH, pause: float = 0) -> None:
        element = self.find(locator, by)
        ActionChains(self.driver).move_to_element(element).double_click().perform()
        if pause:
            time.sleep(pause)

    def hover(self, locator: str, by: str = By.XPATH) -> None:
        element = self.find(locator, by)
        ActionChains(self.driver).move_to_element(element).perform()

    def hover_with_offset(self, locator: str, x_offset: int, y_offset: int, by: str = By.XPATH) -> None:
        element = self.find(locator, by)
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        actions.move_by_offset(x_offset, y_offset).perform()

    def move_to(self, locator: str, by: str = By.XPATH) -> None:
        element = self.find(locator, by)
        ActionChains(self.driver).move_to_element(element).perform()
        time.sleep(self.poll_pause)

    def wait_move_click(self, locator: str, by: str = By.XPATH, timeout: float | None = None) -> None:
        element = self.wait_clickable(locator, by, timeout)
        ActionChains(self.driver).move_to_element(element).perform()
        time.sleep(self.poll_pause)
        element.click()

    def type_text(self, locator: str, text: str, by: str = By.XPATH) -> None:
        self.find(locator, by).send_keys(text)

    def upload_file(self, css_selector: str, path: str) -> None:
        self.driver.find_element(By.CSS_SELECTOR, css_selector).send_keys(path)

    def click_in_new_tab(
        self,
        locator: str,
        check_path: str,
        by: str = By.XPATH,
        check_by: str = By.XPATH,
    ) -> None:
        """Ctrl-click a link, verify the new tab, close it, return to the first tab."""
        element = self.find(locator, by)
        ActionChains(self.driver).key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.wait_present(check_path, check_by)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
```

- [ ] **Step 6: Run the action tests**

Run: `pytest tests/test_browser_actions.py -v`
Expected: PASS (6 passed).

- [ ] **Step 7: Commit**

```bash
git add src/jc_selenium_helper/browser.py tests/fixtures/basic.html tests/fixtures/target.html tests/test_browser_actions.py
git commit -m "feat: add Browser action helpers"
```

---

### Task 6: `Browser` assertions + `fill_in_frame`

**Files:**
- Modify: `src/jc_selenium_helper/browser.py`
- Modify: `tests/fixtures/basic.html` (add checkbox + select)
- Create: `tests/fixtures/frame.html`
- Create: `tests/fixtures/inner.html`
- Test: `tests/test_browser_assertions.py`, `tests/test_browser_frame.py`

**Interfaces:**
- Consumes: `Browser` from Tasks 3–5.
- Produces:
  - `assert_checkbox_checked(locator, by=By.XPATH, timeout=None) -> None`
  - `assert_checkbox_unchecked(locator, by=By.XPATH, timeout=None) -> None`
  - `assert_selected_option(locator, expected_text, by=By.XPATH) -> None`
  - `assert_present(locator, by=By.XPATH) -> None`
  - `fill_in_frame(frame_path, inner_path, text, by=By.XPATH, submit=True) -> None`
  - All assertion failures raise `AssertionError`.

- [ ] **Step 1: Add checkbox and select to the fixture**

Insert inside `<body>` of `tests/fixtures/basic.html`, before `<div id="delayed">`:

```html
    <input id="checked-box" type="checkbox" checked />
    <input id="unchecked-box" type="checkbox" />
    <select id="picker">
      <option>one</option>
      <option selected>two</option>
    </select>
```

- [ ] **Step 2: Create the frame fixtures**

```html
<!-- tests/fixtures/inner.html -->
<!doctype html>
<html>
  <head><title>inner</title></head>
  <body><input id="inner-input" type="text" /></body>
</html>
```

```html
<!-- tests/fixtures/frame.html -->
<!doctype html>
<html>
  <head><title>frame</title></head>
  <body>
    <iframe id="editor" src="inner.html"></iframe>
  </body>
</html>
```

- [ ] **Step 3: Write the failing assertion + frame tests**

```python
# tests/test_browser_assertions.py
import pytest


def test_assert_checkbox_checked_passes(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.assert_checkbox_checked("//input[@id='checked-box']")


def test_assert_checkbox_checked_fails(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    with pytest.raises(AssertionError):
        browser.assert_checkbox_checked("//input[@id='unchecked-box']")


def test_assert_checkbox_unchecked_passes(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.assert_checkbox_unchecked("//input[@id='unchecked-box']")


def test_assert_selected_option_passes(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.assert_selected_option("//select[@id='picker']", "two")


def test_assert_selected_option_fails(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    with pytest.raises(AssertionError):
        browser.assert_selected_option("//select[@id='picker']", "one")


def test_assert_present_fails_when_missing(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    with pytest.raises(AssertionError):
        browser.assert_present("//div[@id='nope']")
```

```python
# tests/test_browser_frame.py
def test_fill_in_frame(browser, fixture_url):
    browser.open(fixture_url("frame.html"))
    browser.fill_in_frame(
        "//iframe[@id='editor']",
        "//input[@id='inner-input']",
        "typed",
        submit=False,
    )
    browser.driver.switch_to.frame(browser.find("//iframe[@id='editor']"))
    assert browser.find("//input[@id='inner-input']").get_attribute("value") == "typed"
    browser.driver.switch_to.default_content()
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `pytest tests/test_browser_assertions.py tests/test_browser_frame.py -v`
Expected: FAIL (AttributeError: no attribute 'assert_checkbox_checked').

- [ ] **Step 5: Add the assertion + frame methods to `Browser`**

Insert after the actions block in `src/jc_selenium_helper/browser.py`:

```python
    # -- assertions --
    def assert_checkbox_checked(self, locator: str, by: str = By.XPATH, timeout: float | None = None) -> None:
        if not self.wait_present(locator, by, timeout).is_selected():
            raise AssertionError(f"Checkbox is not checked: {locator}")

    def assert_checkbox_unchecked(self, locator: str, by: str = By.XPATH, timeout: float | None = None) -> None:
        if self.wait_present(locator, by, timeout).is_selected():
            raise AssertionError(f"Checkbox is checked: {locator}")

    def assert_selected_option(self, locator: str, expected_text: str, by: str = By.XPATH) -> None:
        select = Select(self.find(locator, by))
        actual = select.first_selected_option.text
        if actual != expected_text:
            raise AssertionError(f"Selected option '{actual}' != expected '{expected_text}'")

    def assert_present(self, locator: str, by: str = By.XPATH) -> None:
        if not self.exists(locator, by):
            raise AssertionError(f"Element not present: {locator}")

    # -- frames --
    def fill_in_frame(
        self,
        frame_path: str,
        inner_path: str,
        text: str,
        by: str = By.XPATH,
        submit: bool = True,
    ) -> None:
        """Switch into ``frame_path``, type ``text`` into ``inner_path``, switch back.

        Generic replacement for the app-specific ``switch_and_fill_frame`` (which
        hardcoded the TinyMCE inner path).
        """
        frame = self.find(frame_path, by)
        self.driver.switch_to.frame(frame)
        try:
            self.type_text(inner_path, text)
            if submit:
                self.type_text(inner_path, Keys.RETURN)
        finally:
            self.driver.switch_to.default_content()
```

- [ ] **Step 6: Run the assertion + frame tests**

Run: `pytest tests/test_browser_assertions.py tests/test_browser_frame.py -v`
Expected: PASS (7 passed).

- [ ] **Step 7: Commit**

```bash
git add src/jc_selenium_helper/browser.py tests/fixtures/ tests/test_browser_assertions.py tests/test_browser_frame.py
git commit -m "feat: add Browser assertions and generic fill_in_frame"
```

---

### Task 7: Legacy compatibility adapter

**Files:**
- Create: `src/jc_selenium_helper/legacy.py`
- Test: `tests/test_legacy.py`

**Interfaces:**
- Consumes: `Browser` (all methods) from Tasks 3–6; `rgb_to_hex` from Task 2.
- Produces: `LegacyBrowser(Browser)` exposing the original German/ad-hoc names as deprecated aliases. Each emits `DeprecationWarning`. Importable as `from jc_selenium_helper.legacy import Browser` (module-level alias `Browser = LegacyBrowser`).
- Legacy names mapped: `xpath`→`find`, `xpaths`→`find_all`, `css`→`find(by=CSS)`, `get_elements`→`find_all`, `check_exists_by_xpath`→`exists`, `wait_element_present`→`wait_present`, `wait_element_not_present`→`wait_not_present`, `wait_element_clickable`→`wait_clickable`, `inhalt_geladen`→`wait_document_ready`, `wait_and_click`, `doppelclick_element`→`double_click`, `hover_element`→`hover`, `hover_element_with_offset`→`hover_with_offset`, `move_to_element`→`move_to`, `wait_move_click_element`→`wait_move_click`, `click_new_tab`→`click_in_new_tab`, `eingabe`→`type_text`, `eingabe_upload_css`→`upload_file`, `assert_checkbox_is_checked`→`assert_checkbox_checked`, `assert_checkbox_is_not_checked`→`assert_checkbox_unchecked`, `check_select`→`assert_selected_option`, `ele_test`→`assert_present`, `switch_rgb`→`rgb_to_hex` (static). `seite_geladen` and `switch_and_fill_frame` keep **verbatim original behavior** (AMM refresh loop; hardcoded `//*[@id='tinymce']/p`).

- [ ] **Step 1: Write the failing legacy tests**

```python
# tests/test_legacy.py
import pytest

from jc_selenium_helper.legacy import Browser as LegacyBrowser


def test_legacy_eingabe_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("basic.html"))
    with pytest.warns(DeprecationWarning):
        legacy.eingabe("//input[@id='text-input']", "legacy")
    assert legacy.find("//input[@id='text-input']").get_attribute("value") == "legacy"


def test_legacy_check_exists_by_xpath(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("basic.html"))
    with pytest.warns(DeprecationWarning):
        assert legacy.check_exists_by_xpath("//h1[@id='title']") is True


def test_legacy_switch_rgb_static():
    with pytest.warns(DeprecationWarning):
        assert LegacyBrowser.switch_rgb("rgb(255, 0, 0)") == "#ff0000"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_legacy.py -v`
Expected: FAIL (ModuleNotFoundError: jc_selenium_helper.legacy).

- [ ] **Step 3: Write the legacy adapter**

```python
# src/jc_selenium_helper/legacy.py
"""Backwards-compatible adapter exposing the original German/ad-hoc API.

Existing suites can migrate by replacing::

    from libs.browser import Browser

with::

    from jc_selenium_helper.legacy import Browser

Every legacy method emits a ``DeprecationWarning`` and delegates to the clean
:class:`jc_selenium_helper.browser.Browser` API. Two methods
(``seite_geladen`` and ``switch_and_fill_frame``) keep their original
app-specific behavior verbatim so existing tests are unaffected.
"""

from __future__ import annotations

import time
import warnings

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from jc_selenium_helper.browser import Browser as _Browser
from jc_selenium_helper.colors import rgb_to_hex


def _deprecated(old: str, new: str) -> None:
    warnings.warn(
        f"{old}() is deprecated; use {new}() instead.",
        DeprecationWarning,
        stacklevel=3,
    )


class LegacyBrowser(_Browser):
    """Deprecated German-named API preserved for existing test suites."""

    def xpath(self, xpath):
        _deprecated("xpath", "find")
        return self.find(xpath)

    def xpaths(self, xpath):
        _deprecated("xpaths", "find_all")
        return self.find_all(xpath)

    def css(self, selector):
        _deprecated("css", "find")
        return self.find(selector, by=By.CSS_SELECTOR)

    def get_elements(self, path):
        _deprecated("get_elements", "find_all")
        return self.find_all(path)

    def check_exists_by_xpath(self, path):
        _deprecated("check_exists_by_xpath", "exists")
        return self.exists(path)

    def wait_element_present(self, path, time_to_wait=None):
        _deprecated("wait_element_present", "wait_present")
        return self.wait_present(path, timeout=time_to_wait)

    def wait_element_not_present(self, path, time_to_wait=None):
        _deprecated("wait_element_not_present", "wait_not_present")
        return self.wait_not_present(path, timeout=time_to_wait)

    def wait_element_clickable(self, path, time_to_wait=None):
        _deprecated("wait_element_clickable", "wait_clickable")
        return self.wait_clickable(path, timeout=time_to_wait)

    def inhalt_geladen(self):
        _deprecated("inhalt_geladen", "wait_document_ready")
        return self.wait_document_ready()

    def doppelclick_element(self, pause, hover):
        _deprecated("doppelclick_element", "double_click")
        return self.double_click(hover, pause=pause)

    def hover_element(self, hover):
        _deprecated("hover_element", "hover")
        return self.hover(hover)

    def hover_element_with_offset(self, hover, x_offset, y_offset):
        _deprecated("hover_element_with_offset", "hover_with_offset")
        return self.hover_with_offset(hover, x_offset, y_offset)

    def move_to_element(self, path):
        _deprecated("move_to_element", "move_to")
        return self.move_to(path)

    def wait_move_click_element(self, path, time_to_wait=None):
        _deprecated("wait_move_click_element", "wait_move_click")
        return self.wait_move_click(path, timeout=time_to_wait)

    def click_new_tab(self, path, check_path):
        _deprecated("click_new_tab", "click_in_new_tab")
        return self.click_in_new_tab(path, check_path)

    def eingabe(self, path, text):
        _deprecated("eingabe", "type_text")
        return self.type_text(path, text)

    def eingabe_upload_css(self, path, text):
        _deprecated("eingabe_upload_css", "upload_file")
        return self.upload_file(path, text)

    def assert_checkbox_is_checked(self, path, time_to_wait=None):
        _deprecated("assert_checkbox_is_checked", "assert_checkbox_checked")
        return self.assert_checkbox_checked(path, timeout=time_to_wait)

    def assert_checkbox_is_not_checked(self, path, time_to_wait=None):
        _deprecated("assert_checkbox_is_not_checked", "assert_checkbox_unchecked")
        return self.assert_checkbox_unchecked(path, timeout=time_to_wait)

    def check_select(self, path, exp_text):
        _deprecated("check_select", "assert_selected_option")
        return self.assert_selected_option(path, exp_text)

    def ele_test(self, path):
        _deprecated("ele_test", "assert_present")
        return self.assert_present(path)

    @staticmethod
    def switch_rgb(color_rgb):
        _deprecated("switch_rgb", "colors.rgb_to_hex")
        return rgb_to_hex(color_rgb)

    # -- verbatim app-specific behavior (unchanged for compatibility) --
    def seite_geladen(self, check_path):
        _deprecated("seite_geladen", "wait_page_loaded")
        time_counter = 0
        time.sleep(1)
        while True:
            element = self.driver.find_elements(By.XPATH, check_path)
            if element:
                break
            self.driver.refresh()
            time.sleep(10)
            time_counter += 1
            if time_counter > 5:
                raise ValueError("Seite nicht geladen")
        self.inhalt_geladen()

    def switch_and_fill_frame(self, combined, path, text):
        _deprecated("switch_and_fill_frame", "fill_in_frame")
        time.sleep(combined.settings.k_pause)
        switch_frame = self.driver.find_element(By.XPATH, path)
        self.driver.switch_to.frame(switch_frame)
        tmp_path = "//*[@id='tinymce']/p"
        self.type_text(tmp_path, text)
        self.type_text(tmp_path, Keys.RETURN)
        self.driver.switch_to.default_content()


# Drop-in module-level alias: ``from jc_selenium_helper.legacy import Browser``
Browser = LegacyBrowser
```

- [ ] **Step 4: Run the legacy tests**

Run: `pytest tests/test_legacy.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add src/jc_selenium_helper/legacy.py tests/test_legacy.py
git commit -m "feat: add legacy compatibility adapter"
```

---

### Task 8: pytest plugin

**Files:**
- Create: `src/jc_selenium_helper/plugin.py`
- Test: `tests/test_plugin.py`

**Interfaces:**
- Consumes: `Browser` from Task 3. Registered via the `pytest11` entry point already declared in `pyproject.toml` (Task 1).
- Produces pytest fixtures:
  - `jc_chrome_options() -> selenium...chrome.options.Options` — sensible, overridable defaults.
  - `jc_browser(selenium) -> Browser` — wraps the `pytest-selenium` `selenium` driver fixture.
  - The plugin must import cleanly even if `pytest-selenium` is absent (it only references the `selenium` fixture lazily, at fixture-call time).

- [ ] **Step 1: Write the failing plugin test**

pytest loads the plugin from the installed entry point. Use pytest's `pytester` to run an inner test that only checks fixture availability and Options construction (no real browser needed).

```python
# tests/test_plugin.py
pytest_plugins = ["pytester"]


def test_jc_chrome_options_fixture_available(pytester):
    pytester.makepyfile(
        """
        def test_options(jc_chrome_options):
            args = jc_chrome_options.arguments
            assert "--headless=new" in args
        """
    )
    result = pytester.runpytest("-p", "jc_selenium_helper.plugin")
    result.assert_outcomes(passed=1)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_plugin.py -v`
Expected: FAIL (ModuleNotFoundError: jc_selenium_helper.plugin).

- [ ] **Step 3: Write the plugin**

```python
# src/jc_selenium_helper/plugin.py
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
```

- [ ] **Step 4: Run the plugin test**

Run: `pytest tests/test_plugin.py -v`
Expected: PASS (1 passed).

- [ ] **Step 5: Commit**

```bash
git add src/jc_selenium_helper/plugin.py tests/test_plugin.py
git commit -m "feat: add pytest plugin with jc_browser and jc_chrome_options fixtures"
```

---

### Task 9: Config helper (`config` extra)

**Files:**
- Create: `src/jc_selenium_helper/config.py`
- Test: `tests/test_config.py`

**Interfaces:**
- Produces: `get_settings(location: str | Path, *files: str) -> dynaconf.base.Settings`. Resolves each file relative to `Path(location).parent`, asserts existence, returns a configured `Dynaconf` (environments enabled, prefix `SELENIUM`, switcher `SELENIUM_ENVIRONMENT`).
- Requires the `config` extra (`dynaconf`). Test skips if dynaconf is not installed.

- [ ] **Step 1: Write the failing config test**

```python
# tests/test_config.py
import pytest

pytest.importorskip("dynaconf")

from jc_selenium_helper.config import get_settings  # noqa: E402


def test_get_settings_reads_relative_file(tmp_path):
    (tmp_path / "settings.yaml").write_text("default:\n  greeting: hi\n")
    anchor = tmp_path / "conftest.py"  # any file whose parent holds the settings
    anchor.write_text("")
    settings = get_settings(anchor, "settings.yaml")
    assert settings.greeting == "hi"


def test_get_settings_missing_file_raises(tmp_path):
    anchor = tmp_path / "conftest.py"
    anchor.write_text("")
    with pytest.raises(AssertionError):
        get_settings(anchor, "nope.yaml")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL (ModuleNotFoundError: jc_selenium_helper.config) — or SKIP if dynaconf absent; install with `pip install -e ".[config]"`.

- [ ] **Step 3: Write the config module**

```python
# src/jc_selenium_helper/config.py
"""Optional Dynaconf settings loader (requires the ``config`` extra)."""

from __future__ import annotations

from pathlib import Path

from dynaconf import Dynaconf
from dynaconf.base import Settings


def get_settings(location: str | Path, *files: str) -> Settings:
    """Build a Dynaconf ``Settings`` from files resolved next to ``location``.

    ``location`` is typically ``__file__`` of the caller; each name in ``files``
    is resolved against ``Path(location).parent`` and must exist.
    """
    parent = Path(location).parent
    settings_files = []
    for name in files:
        settings_file = (parent / name).resolve()
        assert settings_file.exists(), f"settings file not found: {settings_file}"
        settings_files.append(settings_file)
    return Dynaconf(
        environments=True,
        envvar_prefix="SELENIUM",
        env_switcher="SELENIUM_ENVIRONMENT",
        settings_files=settings_files,
    )
```

- [ ] **Step 4: Run the config test**

Run: `pip install -e ".[config]" && pytest tests/test_config.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add src/jc_selenium_helper/config.py tests/test_config.py
git commit -m "feat: add optional Dynaconf config loader"
```

---

### Task 10: Axe accessibility helper (`axe` extra)

**Files:**
- Create: `src/jc_selenium_helper/axe.py`
- Test: `tests/test_axe.py`

**Interfaces:**
- Produces:
  - `run_axe(driver) -> dict` — injects axe-core, runs it, returns the raw results dict.
  - `assert_no_violations(driver) -> None` — raises `AssertionError` listing violation ids if any are found.
- Requires the `axe` extra (`axe-selenium-python`). Test skips if absent.

- [ ] **Step 1: Write the failing axe test**

```python
# tests/test_axe.py
import pytest

pytest.importorskip("axe_selenium_python")

from jc_selenium_helper.axe import assert_no_violations, run_axe  # noqa: E402


def test_run_axe_returns_results(driver, fixture_url):
    driver.get(fixture_url("basic.html"))
    results = run_axe(driver)
    assert "violations" in results


def test_assert_no_violations_raises_on_violation(driver, fixture_url):
    # basic.html has an <input> without a label -> at least one violation expected
    driver.get(fixture_url("basic.html"))
    with pytest.raises(AssertionError):
        assert_no_violations(driver)
```

Note: `fixture_url` here is the same fixture defined in `tests/conftest.py`; `driver` is reused directly.

- [ ] **Step 2: Run test to verify it fails**

Run: `pip install -e ".[axe]" && pytest tests/test_axe.py -v`
Expected: FAIL (ModuleNotFoundError: jc_selenium_helper.axe).

- [ ] **Step 3: Write the axe module**

```python
# src/jc_selenium_helper/axe.py
"""Optional accessibility checks via axe-core (requires the ``axe`` extra)."""

from __future__ import annotations

from axe_selenium_python import Axe


def run_axe(driver) -> dict:
    """Inject axe-core into the current page and return the raw results dict."""
    axe = Axe(driver)
    axe.inject()
    return axe.run()


def assert_no_violations(driver) -> None:
    """Run axe-core and raise ``AssertionError`` if any violations are found."""
    results = run_axe(driver)
    violations = results.get("violations", [])
    if violations:
        ids = ", ".join(v["id"] for v in violations)
        raise AssertionError(f"{len(violations)} accessibility violation(s): {ids}")
```

- [ ] **Step 4: Run the axe test**

Run: `pytest tests/test_axe.py -v`
Expected: PASS (2 passed). If `basic.html` produces no violations on the installed axe-core version, adjust the fixture to include a clearly inaccessible element (e.g. an `<img>` without `alt`) so the second test's expectation holds; keep the assertion meaningful.

- [ ] **Step 5: Commit**

```bash
git add src/jc_selenium_helper/axe.py tests/test_axe.py
git commit -m "feat: add optional axe accessibility helper"
```

---

### Task 11: Documentation (MkDocs / Read the Docs)

**Files:**
- Create: `README.md`, `LICENSE`, `CHANGELOG.md`
- Create: `mkdocs.yml`, `.readthedocs.yaml`, `docs/requirements.txt`
- Create: `docs/index.md`, `docs/.pages`
- Create: `docs/getting_started/index.md`, `docs/getting_started/.pages`
- Create: `docs/reference/{index,browser,colors,pytest_plugin,config,axe,migration}.md`, `docs/reference/.pages`
- Create: `docs/development/index.md`

**Interfaces:** none (docs only). Mirrors `../django-crud-views` MkDocs setup (readthedocs theme + awesome-pages).

- [ ] **Step 1: Write `LICENSE` (MIT)**

Standard MIT license text, copyright `2026 Alexander Jacob`.

- [ ] **Step 2: Write `mkdocs.yml`**

```yaml
site_name: jc-selenium-helper
theme: readthedocs
plugins:
  - search
  - awesome-pages
repo_url: https://github.com/jacob-consulting/jc-selenium-helper
edit_uri: blob/main/docs/
```

- [ ] **Step 3: Write `.readthedocs.yaml`**

```yaml
version: 2

build:
  os: ubuntu-24.04
  tools:
    python: "3.12"

mkdocs:
  configuration: mkdocs.yml

python:
  install:
    - requirements: docs/requirements.txt
```

- [ ] **Step 4: Write `docs/requirements.txt`**

```text
mkdocs>=1.6.1
mkdocs-awesome-pages-plugin>=2.10.1
```

- [ ] **Step 5: Write the docs pages**

`docs/index.md` — overview + install:

```markdown
# jc-selenium-helper

Selenium WebDriver helper utilities for writing browser tests.

## Install

```bash
pip install jc-selenium-helper            # core (selenium only)
pip install "jc-selenium-helper[pytest]"  # + pytest fixtures
pip install "jc-selenium-helper[config]"  # + Dynaconf settings loader
pip install "jc-selenium-helper[axe]"     # + accessibility checks
pip install "jc-selenium-helper[all]"     # everything
```
```

`docs/getting_started/index.md` — quickstart:

```markdown
# Getting Started

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from jc_selenium_helper import Browser

driver = webdriver.Chrome()
browser = Browser(driver, default_timeout=30)

browser.open("https://example.com")
browser.wait_and_click("//a[@id='more']")           # XPath by default
browser.type_text("#search", "hello", by=By.CSS_SELECTOR)
```

Locators default to XPath. Pass `by=By.CSS_SELECTOR` to switch strategy.
```

`docs/reference/browser.md` — document each Browser method group (finders, waits, actions, assertions, frame) with signatures and one example each, drawn from the Task 3–6 interfaces.

`docs/reference/colors.md` — `rgb_to_hex`.

`docs/reference/pytest_plugin.md` — `jc_browser`, `jc_chrome_options`, how to override options.

`docs/reference/config.md` — `get_settings`.

`docs/reference/axe.md` — `run_axe`, `assert_no_violations`.

`docs/reference/migration.md` — table mapping every legacy German name to its new equivalent (copy the mapping from Task 7's interface block), plus the one-line import swap.

`docs/development/index.md` — clone, `pip install -e ".[test]"`, run `nox`, build docs with `mkdocs serve`.

Add `.pages` files for awesome-pages ordering, e.g. `docs/.pages`:

```yaml
nav:
  - index.md
  - getting_started
  - reference
  - development
```

- [ ] **Step 6: Write `README.md` and `CHANGELOG.md`**

`README.md`: short description, install matrix (as above), a 6-line quickstart, links to docs and PyPI, license line. `CHANGELOG.md`: a `## 0.1.0` section listing the initial feature set.

- [ ] **Step 7: Verify the docs build**

Run:
```bash
pip install -e ".[dev]"
mkdocs build --strict
```
Expected: build succeeds with no warnings (strict).

- [ ] **Step 8: Commit**

```bash
git add README.md LICENSE CHANGELOG.md mkdocs.yml .readthedocs.yaml docs/
git commit -m "docs: add MkDocs documentation and Read the Docs config"
```

---

### Task 12: Tooling & CI

**Files:**
- Create: `noxfile.py`
- Create: `.pre-commit-config.yaml`
- Create: `.github/workflows/ci.yml`
- Modify: `pyproject.toml` (add `[tool.bumpversion]` config)

**Interfaces:** none (project tooling). CI runs lint + tests; a docs-build job mirrors Read the Docs.

- [ ] **Step 1: Write `noxfile.py`**

```python
# noxfile.py
import nox

PYTHONS = ["3.12", "3.13", "3.14"]


@nox.session(python=PYTHONS)
def tests(session):
    session.install("-e", ".[test]")
    session.run("pytest", "-q", *session.posargs)


@nox.session
def lint(session):
    session.install("ruff")
    session.run("ruff", "check", "src", "tests")
    session.run("ruff", "format", "--check", "src", "tests")


@nox.session
def docs(session):
    session.install("-e", ".[dev]")
    session.run("mkdocs", "build", "--strict")
```

- [ ] **Step 2: Write `.pre-commit-config.yaml`**

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

- [ ] **Step 3: Add bump-my-version config to `pyproject.toml`**

Append:

```toml
[tool.bumpversion]
current_version = "0.1.0"
allow_dirty = false
commit = true
tag = true

[[tool.bumpversion.files]]
filename = "pyproject.toml"
search = 'version = "{current_version}"'
replace = 'version = "{new_version}"'

[[tool.bumpversion.files]]
filename = "src/jc_selenium_helper/__init__.py"
search = '__version__ = "{current_version}"'
replace = '__version__ = "{new_version}"'
```

- [ ] **Step 4: Write `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install ruff
      - run: ruff check src tests
      - run: ruff format --check src tests

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - uses: browser-actions/setup-chrome@v1
      - run: pip install -e ".[test]"
      - run: pytest -q

  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: mkdocs build --strict
```

- [ ] **Step 5: Verify lint and full test suite locally**

Run:
```bash
pip install -e ".[test]" ruff
ruff check src tests
ruff format --check src tests
pytest -q
```
Expected: ruff clean; all tests pass (run `ruff format src tests` first if the check reports diffs, then re-commit).

- [ ] **Step 6: Commit**

```bash
git add noxfile.py .pre-commit-config.yaml .github/workflows/ci.yml pyproject.toml
git commit -m "chore: add nox, pre-commit, bump-my-version, and CI"
```

---

## Self-Review

**Spec coverage:**
- Package identity/layout → Task 1. ✓
- Clean `Browser` API (finders/waits/actions/assertions/frame, XPath+`by=`, configurable timeouts) → Tasks 3–6. ✓
- Generalized `fill_in_frame` + `wait_page_loaded` → Tasks 6 & 4. ✓
- `colors.rgb_to_hex` replacing colormap/easydev → Task 2. ✓
- Legacy adapter with deprecation + verbatim app-specific methods → Task 7. ✓
- pytest plugin (`pytest` extra, entry point) → Task 8 (entry point declared in Task 1). ✓
- config loader (`config` extra) → Task 9. ✓
- axe helper (`axe` extra) → Task 10. ✓
- Extras `pytest`/`config`/`axe`/`all`/`dev`/`test`; core = selenium only → Task 1. ✓
- MkDocs + Read the Docs, migration page → Task 11. ✓
- Tooling (ruff, nox, pre-commit, bump-my-version, CI) → Task 12. ✓
- Test strategy: local HTML fixtures + headless Chrome, matrix 3.12–3.14 → Tasks 3–10, 12. ✓

**Placeholder scan:** No "TBD"/"implement later". Docs Task 11 Steps 5–6 describe per-page content rather than full verbatim prose; this is documentation copy, not code, and each page's required content and source (the interface blocks) are named. Acceptable for a docs task.

**Type consistency:** Method names are consistent across tasks and the legacy mapping (e.g. `wait_present`, `wait_clickable`, `type_text`, `assert_checkbox_checked`, `fill_in_frame`) match between `browser.py` (Tasks 3–6), `legacy.py` (Task 7), plugin (Task 8), and docs (Task 11). `timeout=None → default_timeout` convention is uniform across waits/assertions.

**Known environmental dependency:** All Browser/plugin/axe tests require Chrome + a matching chromedriver on PATH (Selenium 4 Manager resolves the driver automatically when Chrome is present). CI installs Chrome via `browser-actions/setup-chrome`.
