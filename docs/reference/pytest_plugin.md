# Pytest plugin

Installing the `pytest` extra (`pip install "jc-selenium-helper[pytest]"`)
registers a pytest plugin via the `pytest11` entry point, so it is picked up
automatically — no explicit `pytest_plugins` entry needed. It depends on
[pytest-selenium](https://pytest-selenium.readthedocs.io/) for the underlying
WebDriver management.

Fixtures are namespaced with a `jc_` prefix so they don't clash with a
project's own `browser`/`chrome_options` fixtures.

## `jc_chrome_options`

Sensible default headless Chrome options:

- `--headless=new`
- `--disable-gpu`
- `--ignore-certificate-errors`
- `--no-sandbox`
- `--disable-dev-shm-usage`

Override it in your project's `conftest.py` to customize (e.g. add
arguments, run non-headless, etc.):

```python
import pytest

@pytest.fixture
def jc_chrome_options(jc_chrome_options):
    jc_chrome_options.add_argument("--window-size=1920,1080")
    return jc_chrome_options
```

## `jc_browser`

Wraps the `selenium` fixture (provided by `pytest-selenium`) in a
`jc_selenium_helper.Browser`:

```python
def jc_browser(selenium) -> Browser:
    return Browser(selenium)
```

Use it directly in tests:

```python
def test_homepage(jc_browser):
    jc_browser.open("https://example.com")
    jc_browser.assert_present("//h1")
```
