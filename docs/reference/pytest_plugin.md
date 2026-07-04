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

### Insecure flags are opt-in

`--no-sandbox` and `--ignore-certificate-errors` weaken Chrome's security
(they disable the browser sandbox and TLS certificate verification). They are
**off by default**. Some sandboxed CI containers need them, so you can opt in
two ways — either one enables the flags **and** emits an
`InsecureChromeOptionsWarning`:

- Set the `JC_SELENIUM_INSECURE` environment variable (to `1`, `true`, `yes`,
  or `on`) — handy for a single CI run:

  ```bash
  JC_SELENIUM_INSECURE=1 pytest
  ```

- Or override the `jc_insecure_chrome` fixture in your `conftest.py`:

  ```python
  import pytest

  @pytest.fixture
  def jc_insecure_chrome():
      return True
  ```

## `jc_insecure_chrome`

Boolean fixture, default `False`. Return `True` (or set `JC_SELENIUM_INSECURE`)
to add the insecure Chrome flags to `jc_chrome_options`. Opting in triggers an
`InsecureChromeOptionsWarning`.

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
