# Legacy Coverage Backfill — Design

## Problem

Total coverage sits at 80% (the configured floor), but that number hides an
uneven split:

- `src/jc_selenium_helper/legacy.py`: **44%** (51 of 91 lines uncovered).
  Only 3 of `LegacyBrowser`'s ~23 deprecated delegate methods have tests
  (`eingabe`, `check_exists_by_xpath`, `switch_rgb`).
- `src/jc_selenium_helper/browser.py`: **96%** (5 lines uncovered): the
  timeout-exceeded branch in `wait_document_ready` (lines 72-75) and the
  `pause` branch in `double_click` (line 106).

Every other module (`__init__.py`, `axe.py`, `colors.py`, `config.py`,
`plugin.py`) is already at 100%.

## Goal

Backfill tests for the untested `legacy.py` delegate methods and the two
remaining `browser.py` branches, raising total coverage from 80% into the
high 90s. Not a refactor — no production code changes, only new tests.

## Approach

### legacy.py

Each `LegacyBrowser` method has exactly two responsibilities: emit a
`DeprecationWarning` and forward to the corresponding modern `Browser`
method. The modern methods already have full behavioral coverage (happy
and failure paths) in `tests/test_browser_*.py`, so these new tests only
need to prove delegation + warning — one happy-path call per method is
enough; re-testing failure branches here would be duplicate coverage of
code this suite already exercises.

Tests are added to the existing `tests/test_legacy.py`, matching its
current style exactly: construct `LegacyBrowser(driver, default_timeout=10,
poll_pause=0.2)` directly, open a fixture page, wrap the call in
`pytest.warns(DeprecationWarning)`, assert one behavioral outcome. No
mocking — consistent with the rest of the suite (mocking appears only in
`test_plugin.py`, which is unrelated).

Methods to cover, and which existing fixture page/element they reuse:

| Method | Fixture page / element | Delegates to |
|---|---|---|
| `xpath` | basic.html `#title` | `find` |
| `xpaths` | basic.html `.item` (3 elements) | `find_all` |
| `css` | basic.html `#title` | `find` (by=CSS_SELECTOR) |
| `get_elements` | basic.html `.item` | `find_all` |
| `wait_element_present` | basic.html `#late` (appears ~500ms) | `wait_present` |
| `wait_element_not_present` | dynamic.html `#vanishing` (disappears ~300ms) | `wait_not_present` |
| `wait_element_clickable` | basic.html `#btn` | `wait_clickable` |
| `inhalt_geladen` | basic.html | `wait_document_ready` |
| `doppelclick_element` | basic.html `#dbl` | `double_click` |
| `hover_element` | dynamic.html `#hover-target` | `hover` |
| `hover_element_with_offset` | offset.html `#anchor` → `#offset-target` | `hover_with_offset` |
| `move_to_element` | dynamic.html `#hover-target` | `move_to` |
| `wait_move_click_element` | basic.html `#clickable` | `wait_move_click` |
| `click_new_tab` | basic.html `#newtab` → target.html | `click_in_new_tab` |
| `eingabe_upload_css` | dynamic.html `#upload` | `upload_file` |
| `assert_checkbox_is_checked` | basic.html `#checked-box` | `assert_checkbox_checked` |
| `assert_checkbox_is_not_checked` | basic.html `#unchecked-box` | `assert_checkbox_unchecked` |
| `check_select` | basic.html `#picker` ("two") | `assert_selected_option` |
| `ele_test` | basic.html `#title` | `assert_present` |
| `seite_geladen` | basic.html `#title` (present immediately, no refresh loop) | `inhalt_geladen` |

`seite_geladen`'s failure path (refresh loop, up to 5 retries with a
hardcoded `sleep(10)` between attempts) is intentionally **not** tested:
it would add 50+ seconds to the suite to cover one already-understood
`ValueError` branch. Only the success path (element present on first
check) is tested.

### browser.py

Two tests added to the existing behavior files:

- `tests/test_browser_waits.py`: force `document.readyState` to stay
  `"loading"` via `driver.execute_script("Object.defineProperty(document,
  'readyState', {get: () => 'loading'})")` on a loaded page, then call
  `wait_document_ready(timeout=<short>)` and assert it raises
  `TimeoutError`. This is a real-browser DOM override, not a Python-side
  mock, so it's consistent with the project's no-mocking convention for
  browser behavior.
- `tests/test_browser_actions.py`: call `double_click(..., pause=0.1)` on
  the existing `#dbl` button fixture and assert the click still registers.

## Non-goals

- No changes to `fail_under` in `pyproject.toml` as part of this work.
  Once the new coverage number is known, raising the floor is a separate
  follow-up decision.
- No production code changes — `legacy.py` and `browser.py` behavior is
  unchanged, only test coverage.

## Expected outcome

- `legacy.py`: 44% → ~100%
- `browser.py`: 96% → 100%
- Total: 80% → ~97-99%
- All existing tests continue to pass; new tests follow the current
  suite's conventions (real headless Chrome, fixture HTML pages, no
  mocking).
