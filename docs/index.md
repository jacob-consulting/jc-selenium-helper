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

## Where to go next

- [Getting Started](getting_started/index.md) for a quickstart.
- [Reference](reference/index.md) for the full API.
- [Development](development/index.md) to contribute.

Migrating an existing suite from the old German-named `libs.browser.Browser`?
See [Migration](reference/migration.md).
