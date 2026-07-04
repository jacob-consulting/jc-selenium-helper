# Axe

Optional accessibility checks via [axe-core](https://github.com/dequelabs/axe-core)
(requires the `axe` extra: `pip install "jc-selenium-helper[axe]"`), using the
[axe-selenium-python](https://pypi.org/project/axe-selenium-python/) bindings.

### `run_axe(driver) -> dict`

Injects axe-core into the current page and returns the raw results dict.

```python
from jc_selenium_helper.axe import run_axe

results = run_axe(driver)
results["violations"]
```

### `assert_no_violations(driver) -> None`

Runs axe-core and raises `AssertionError` (listing the violation IDs) if any
violations were found.

```python
from jc_selenium_helper.axe import assert_no_violations

def test_homepage_is_accessible(jc_browser):
    jc_browser.open("https://example.com")
    assert_no_violations(jc_browser.driver)
```
