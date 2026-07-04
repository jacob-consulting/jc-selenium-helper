# jc-selenium-helper — Package Design

**Date:** 2026-07-04
**Author:** Alexander Jacob
**Status:** Approved design, ready for implementation planning

## Purpose

Turn a tester's internal Selenium utility files (`browser.py`, `config.py`,
`utils.py`, `conftest.py`) into a reusable, documented, publishable Python
package: **`jc-selenium-helper`** (import name `jc_selenium_helper`).

The package is published to PyPI with Read the Docs / MkDocs (Markdown)
documentation, mirroring the packaging conventions of the sibling project
`../django-crud-views`.

## Goals

- A clean, consistent, English public API for the `Browser` Selenium wrapper.
- A drop-in migration path for the existing internal test suite (which imports
  `from libs.browser import Browser` and uses German method names) via a
  deprecated compatibility adapter.
- Optional, cleanly separated capabilities (pytest plugin, config loader,
  accessibility helper) behind dependency extras.
- Standard packaging, docs, and tooling matching `django-crud-views`.

## Non-goals

- Rewriting the tester's actual test suite (only providing the compat shim so
  it keeps working).
- Supporting drivers other than Selenium WebDriver.
- Bundling app/domain-specific YAML settings (AMM/Arbeitsagentur test
  environments). Those stay in the consuming project.

## Assessment of the source material

| File | Content | Disposition |
|---|---|---|
| `browser.py` | `Browser` class, ~30 helper methods wrapping a Selenium `WebDriver`. Mixed German/English names; a few app-specific assumptions. | Core asset. Clean up → `browser.py`; preserve old behavior in `legacy.py`. |
| `config.py` | Dynaconf loader hardcoded to specific YAML files (AMM domain). | Not reusable as-is. Superseded by generic `config.get_settings()`. |
| `utils.py` | Generic `get_settings(location, *files)` Dynaconf loader. | Becomes `config.py` (behind `config` extra). |
| `conftest.py` | pytest fixtures: `browser`, `chrome_options`, `settings`. Opinionated Chrome options (headless, no-sandbox, fixed screen size). | Becomes `plugin.py` pytest plugin (behind `pytest` extra); options made configurable. |
| `*.yaml` | App/domain-specific test settings. | Out of scope; stays in consuming project. |

### Issues identified and their resolution

1. **Mixed German/English naming** (`eingabe`, `doppelclick_element`,
   `seite_geladen`, `inhalt_geladen`). → Clean English public API; German names
   preserved as deprecated aliases in the legacy adapter.
2. **App-specific logic leaks** — `switch_and_fill_frame` hardcodes
   `//*[@id='tinymce']/p`; `seite_geladen` runs an AMM-specific
   refresh-on-proxy-error loop. → Generalized (parametrized) in core; original
   verbatim behavior kept in `legacy.py`.
3. **Heavy dependency for one function** — `colormap` + `easydev` used only for
   `rgb2hex` in `switch_rgb`. → Replaced by a small `colors.rgb_to_hex()`;
   dependencies dropped.
4. **Hardcoded configuration** — `max_wait_time_s = 120`, sprinkled
   `time.sleep`. → Constructor-configurable (`default_timeout`, `poll_pause`).
5. **XPath-only locators** with ad-hoc CSS variants. → XPath default with an
   optional `by=` argument.

## Package identity & layout

- **PyPI name:** `jc-selenium-helper`  **Import name:** `jc_selenium_helper`
- **Layout:** `src/` layout, single importable package with focused modules
  (not the multi-package split used by `django-crud-views` — this project is
  smaller).
- **Python:** ≥ 3.12 (tested 3.12–3.14).
- **License:** MIT.
- **Docs:** MkDocs (`readthedocs` theme + `awesome-pages`), Markdown, on Read
  the Docs.
- **Tooling:** ruff, pre-commit, nox, bump-my-version, GitHub Actions.

```
jc-selenium-helper/
├── pyproject.toml
├── README.md  LICENSE  CHANGELOG.md
├── mkdocs.yml  .readthedocs.yaml  noxfile.py
├── .pre-commit-config.yaml  .gitignore
├── src/jc_selenium_helper/
│   ├── __init__.py        # exports Browser, __version__
│   ├── browser.py         # clean Browser (core)
│   ├── legacy.py          # LegacyBrowser adapter (deprecated German aliases)
│   ├── waits.py           # wait / page-load helpers (internal split of browser)
│   ├── colors.py          # rgb_to_hex (replaces colormap/easydev)
│   ├── plugin.py          # pytest plugin           [extra: pytest]
│   ├── config.py          # get_settings() Dynaconf loader   [extra: config]
│   ├── axe.py             # accessibility helper     [extra: axe]
│   └── py.typed
├── tests/
│   └── fixtures/          # local HTML pages exercised by headless Chrome
└── docs/
    ├── index.md
    ├── getting_started/   # install, quickstart
    ├── reference/         # one page per API area
    └── development/       # contributing, release
```

## Module & API design

### `browser.py` — `Browser` (core)

Cleaned English API. Constructor makes previously-hardcoded values
configurable:

```python
Browser(driver, default_timeout=120, poll_pause=1)
```

- **Locators:** XPath by default; every locator-taking method accepts an
  optional `by=` argument.

  ```python
  browser.wait_and_click("//button[@id='save']")
  browser.wait_and_click(".btn-save", by=By.CSS_SELECTOR)
  ```

- **Method groups and renames** (old → new):

  | Group | Old (German/ad-hoc) | New (English) |
  |---|---|---|
  | Finders | `xpath`, `xpaths`, `css`, `get_elements`, `check_exists_by_xpath` | `find`, `find_all`, `find` (via `by=`), `find_all`, `exists` |
  | Waits | `wait_element_present`, `wait_element_not_present`, `wait_element_clickable`, `inhalt_geladen`, `seite_geladen` | `wait_present`, `wait_not_present`, `wait_clickable`, `wait_document_ready`, `wait_page_loaded` |
  | Actions | `wait_and_click`, `doppelclick_element`, `hover_element`, `hover_element_with_offset`, `move_to_element`, `wait_move_click_element`, `click_new_tab`, `eingabe`, `eingabe_upload_css` | `wait_and_click`, `double_click`, `hover`, `hover_with_offset`, `move_to`, `wait_move_click`, `click_in_new_tab`, `type_text`, `upload_file` |
  | Assertions | `assert_checkbox_is_checked`, `assert_checkbox_is_not_checked`, `check_select`, `ele_test` | `assert_checkbox_checked`, `assert_checkbox_unchecked`, `assert_selected_option`, `assert_present` |
  | Frame | `switch_and_fill_frame` | `fill_in_frame(frame_path, inner_path, text)` |

  (Exact final names to be confirmed during implementation; the table sets the
  direction: consistent English, no hardcoded inner paths.)

- **Generalized methods** (app assumptions removed):
  - `fill_in_frame(frame_path, inner_path, text)` — inner element path is a
    parameter, not the hardcoded TinyMCE path.
  - `wait_page_loaded(check_path, retries=5, interval=10)` — generic
    wait-with-retry (refresh on absence), configurable retries/interval, no
    AMM-specific comments.

- **`waits.py`** may hold the wait/page-load implementations imported by
  `Browser`, keeping `browser.py` focused. Internal organization detail; the
  public surface is `Browser`.

### `legacy.py` — `LegacyBrowser(Browser)`

Subclass exposing the original German/ad-hoc method names as thin wrappers that
emit `DeprecationWarning` and delegate to the new methods. `switch_and_fill_frame`
and `seite_geladen` reproduce the **original verbatim behavior** (hardcoded
TinyMCE path, AMM refresh loop) so the existing suite is unaffected.

Migration for the tester: replace
`from libs.browser import Browser` with
`from jc_selenium_helper.legacy import Browser`. Nothing else changes.

### `colors.py`

`rgb_to_hex(rgb_string)` — parses a CSS `rgb(...)` string to `#rrggbb` using the
standard library. Replaces the `colormap`/`easydev` dependency. The old
`Browser.switch_rgb` becomes a legacy alias.

### `plugin.py` — pytest plugin  `[extra: pytest]`

Registered via the `pytest11` entry point so installing the extra makes the
fixtures available with no `conftest` wiring:

- `browser` — yields a `Browser` wrapping the `selenium` fixture.
- `chrome_options` — sensible defaults, **overridable** rather than hardcoded
  (headless, no-sandbox, screen size become opt-in / configurable).
- `settings` — optional; integrates with the config helper when present.

Depends on `pytest`, `pytest-selenium`.

### `config.py` — `get_settings()`  `[extra: config]`

Generic Dynaconf loader (from `utils.py`):
`get_settings(location, *files) -> Settings`. Kept out of the core so the base
install needs only Selenium. Depends on `dynaconf`.

### `axe.py` — accessibility helper  `[extra: axe]`

Thin wrapper over `axe-selenium-python`, e.g. `run_axe(driver) -> violations`,
for accessibility assertions in tests. Depends on `axe-selenium-python`.

## Dependencies & extras

- **Core:** `selenium`.
- **Extras:**
  - `pytest` → `pytest`, `pytest-selenium`
  - `config` → `dynaconf`
  - `axe` → `axe-selenium-python`
  - `all` → `jc-selenium-helper[pytest,config,axe]`
  - `dev` → ruff, pre-commit, bump-my-version, mkdocs, mkdocs-awesome-pages-plugin
  - `test` → nox, pytest, pytest-xdist, pytest-cov
- **Dropped:** `colormap`, `easydev`.

## Documentation

MkDocs mirroring `django-crud-views`:

- `docs/index.md` — overview, install.
- `docs/getting_started/` — install, quickstart (create a driver → wrap in
  `Browser` → drive a page).
- `docs/reference/` — one page per area: browser (finders/waits/actions/
  assertions), colors, pytest-plugin, config, axe, and a **migration/legacy**
  page mapping old → new names.
- `docs/development/` — contributing, running tests, release process.
- `.readthedocs.yaml` + `docs/requirements.txt`; `mkdocs.yml` with the
  `readthedocs` theme and `awesome-pages` plugin.

## Testing strategy

- Unit/integration tests drive **local HTML fixtures** (`tests/fixtures/*.html`)
  via headless Chrome, so every helper is exercised for real without an external
  application.
- Cover: finders, each wait, each action, assertions (pass and fail paths),
  `fill_in_frame`, `wait_page_loaded` retry logic, `colors.rgb_to_hex`, and the
  legacy adapter (deprecation warnings + delegation).
- `nox` matrix over Python 3.12–3.14; ruff lint/format in CI; docs build check.

## Release & tooling

- `bump-my-version` for versioning; `CHANGELOG.md` maintained.
- GitHub Actions: lint, test matrix, docs build; publish to PyPI on tag.
- pre-commit: ruff (lint + format).

## Open items for implementation

- Finalize the exact new method names against the table above.
- Decide whether `waits.py` is a separate module or stays inline in
  `browser.py` (organizational, no API impact).
- Confirm minimum Selenium version.
