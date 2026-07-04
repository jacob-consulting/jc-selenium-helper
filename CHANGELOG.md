# Changelog

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
