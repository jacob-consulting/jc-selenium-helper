# Changelog

## Unreleased

### Changed

- **Removed the plugin-level `chrome_options` fixture.** It was meant to feed
  `jc_chrome_options` into pytest-selenium's driver automatically, but
  plugin-vs-plugin fixture precedence is not deterministic across environments,
  so the wiring was unreliable (it worked in some installs and silently used
  pytest-selenium's own defaults in others). To feed the defaults in, add a
  one-line `chrome_options` override to your project `conftest.py` (a conftest
  fixture reliably takes precedence):

  ```python
  @pytest.fixture
  def chrome_options(jc_chrome_options):
      return jc_chrome_options
  ```

## 0.2.0

### Changed

- **Insecure Chrome flags are now opt-in.** The `jc_chrome_options` fixture no
  longer adds `--no-sandbox` or `--ignore-certificate-errors` by default (they
  disable the browser sandbox and TLS verification). Opt in by setting the
  `JC_SELENIUM_INSECURE` environment variable or overriding the new
  `jc_insecure_chrome` fixture to return `True`; enabling them emits an
  `InsecureChromeOptionsWarning`.

## 0.1.0

Initial release.

- `Browser`: a thin, ergonomic wrapper around a Selenium `WebDriver`, with
  XPath-by-default locators (override via `by=`):
  - Finders: `find`, `find_all`, `exists`.
  - Waits: `wait_present`, `wait_clickable`, `wait_not_present`,
    `wait_document_ready`, `wait_page_loaded`.
  - Actions: `wait_and_click`, `double_click`, `hover`, `hover_with_offset`,
    `move_to`, `wait_move_click`, `type_text`, `upload_file`,
    `click_in_new_tab`.
  - Assertions: `assert_checkbox_checked`, `assert_checkbox_unchecked`,
    `assert_selected_option`, `assert_present`.
  - Frames: `fill_in_frame`.
- `jc_selenium_helper.colors.rgb_to_hex`: convert a CSS `rgb()`/`rgba()`
  string to `#rrggbb`.
- Optional `pytest` extra: a pytest plugin (`pytest11` entry point) providing
  the `jc_chrome_options` and `jc_browser` fixtures, built on
  `pytest-selenium`.
- Optional `config` extra: `jc_selenium_helper.config.get_settings`, a
  Dynaconf settings loader.
- Optional `axe` extra: `jc_selenium_helper.axe.run_axe` and
  `assert_no_violations`, accessibility checks via axe-core.
- `jc_selenium_helper.legacy.Browser`: a backwards-compatible adapter exposing
  the original German-named API, for migrating existing suites with a
  one-line import swap. See the
  [migration guide](https://jc-selenium-helper.readthedocs.io/reference/migration/).
