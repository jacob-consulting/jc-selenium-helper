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

## Using the pytest fixtures

Installing the `pytest` extra registers a pytest plugin (via `pytest11`) that
provides a ready-made `jc_browser` fixture built on top of
[pytest-selenium](https://pytest-selenium.readthedocs.io/)'s `selenium` fixture:

```python
def test_homepage(jc_browser):
    jc_browser.open("https://example.com")
    jc_browser.assert_present("//h1")
```

See [pytest plugin](../reference/pytest_plugin.md) for details on the fixtures
and how to override the default Chrome options.

## Next steps

- Browse the [Reference](../reference/index.md) for the full API.
- Migrating an existing suite? See [Migration](../reference/migration.md).
