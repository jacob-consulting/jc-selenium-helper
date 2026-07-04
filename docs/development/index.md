# Development

## Setup

```bash
git clone https://github.com/jacob-consulting/jc-selenium-helper.git
cd jc-selenium-helper
pip install -e ".[test]"
```

## Running the tests

```bash
nox
```

Or invoke `pytest` directly against a single environment:

```bash
pytest
```

## Building the documentation

```bash
pip install -e ".[dev]"
mkdocs serve
```

This serves the docs locally with live reload. To produce a static build:

```bash
mkdocs build --strict
```

## Project layout

- `src/jc_selenium_helper/` — the package (`browser.py`, `colors.py`,
  `plugin.py`, `config.py`, `axe.py`, `legacy.py`).
- `tests/` — the pytest suite.
- `docs/` — this documentation, built with MkDocs and published to
  Read the Docs.
