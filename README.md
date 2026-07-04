# jc-selenium-helper

Selenium WebDriver helper utilities for writing browser tests.

`Browser` wraps a Selenium `WebDriver` with concise, XPath-by-default finders,
waits, actions, assertions, and frame handling. Optional extras add a ready-made
pytest fixture, a Dynaconf settings loader, and axe-core accessibility checks.

## Install

```bash
pip install jc-selenium-helper            # core (selenium only)
pip install "jc-selenium-helper[pytest]"  # + pytest fixtures
pip install "jc-selenium-helper[config]"  # + Dynaconf settings loader
pip install "jc-selenium-helper[axe]"     # + accessibility checks
pip install "jc-selenium-helper[all]"     # everything
```

## Quickstart

```python
from selenium import webdriver
from jc_selenium_helper import Browser

driver = webdriver.Chrome()
browser = Browser(driver, default_timeout=30)

browser.open("https://example.com")
browser.wait_and_click("//a[@id='more']")  # XPath by default
```

## Links

- Full documentation: https://jc-selenium-helper.readthedocs.io
- PyPI: https://pypi.org/project/jc-selenium-helper/
- Source: https://github.com/jacob-consulting/jc-selenium-helper

## License

MIT — see [LICENSE](LICENSE).
