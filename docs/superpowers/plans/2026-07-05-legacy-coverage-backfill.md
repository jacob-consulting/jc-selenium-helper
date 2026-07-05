# Legacy Coverage Backfill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Backfill tests for `LegacyBrowser`'s untested deprecated delegate methods and the 2 remaining uncovered branches in `Browser`, raising total coverage from 80% into the high 90s.

**Architecture:** No production code changes. Each task adds test functions to existing test files (`tests/test_legacy.py`, `tests/test_browser_waits.py`, `tests/test_browser_actions.py`), reusing existing fixture pages under `tests/fixtures/`.

**Tech Stack:** pytest, Selenium (headless Chrome via the session-scoped `driver` fixture in `tests/conftest.py`), `coverage[toml]`.

## Global Constraints

- No production code changes — `src/jc_selenium_helper/legacy.py` and `src/jc_selenium_helper/browser.py` behavior stays exactly as-is; only tests are added.
- No changes to `fail_under` in `pyproject.toml` as part of this plan.
- No mocking — every test drives a real headless Chrome instance against a real fixture HTML page, matching the existing suite's convention (mocking appears only in `test_plugin.py`, which is unrelated).
- Legacy tests construct `LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)` directly (not the `browser` fixture, which returns a plain `Browser`), matching the existing tests in `tests/test_legacy.py`.
- **This is a test-only backfill, not new-feature TDD.** The production code already implements the behavior under test, so "run the test" steps below expect an immediate PASS (proving delegation + warning work), not a RED→GREEN cycle. Each task's final verification is a `coverage report -m` showing the target lines are no longer listed as missing.
- Full suite must stay green and the coverage gate (`fail_under = 80`) must keep passing after every task.

---

### Task 1: browser.py — cover the 2 remaining branches

**Files:**
- Modify: `tests/test_browser_waits.py` (append test)
- Modify: `tests/test_browser_actions.py` (append test)

**Interfaces:**
- Consumes: `Browser.wait_document_ready(timeout: float | None = None) -> None` (src/jc_selenium_helper/browser.py:68-75), `Browser.double_click(locator: str, by: str = By.XPATH, pause: float = 0) -> None` (src/jc_selenium_helper/browser.py:102-106), the `browser` and `fixture_url` fixtures from `tests/conftest.py`.
- Produces: nothing new for later tasks.

- [ ] **Step 1: Add the `wait_document_ready` timeout test**

Append to `tests/test_browser_waits.py`:

```python
def test_wait_document_ready_times_out(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.driver.execute_script(
        "Object.defineProperty(document, 'readyState', {get: () => 'loading'});"
    )
    with pytest.raises(TimeoutError, match="readyState"):
        browser.wait_document_ready(timeout=0.3)
```

- [ ] **Step 2: Add the `double_click` pause test**

Append to `tests/test_browser_actions.py`:

```python
def test_double_click_with_pause(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.double_click("//button[@id='dbl']", pause=0.1)
    assert browser.find("//button[@id='dbl']").text == "double"
```

- [ ] **Step 3: Run both new tests**

Run: `python -m pytest tests/test_browser_waits.py::test_wait_document_ready_times_out tests/test_browser_actions.py::test_double_click_with_pause -v`
Expected: both PASS.

- [ ] **Step 4: Confirm coverage for browser.py**

Run: `python -m coverage run -m pytest -q && python -m coverage report -m`
Expected: `src/jc_selenium_helper/browser.py` shows `100%` with no `Missing` lines listed.

- [ ] **Step 5: Commit**

```bash
git add tests/test_browser_waits.py tests/test_browser_actions.py
git commit -m "test: cover wait_document_ready timeout and double_click pause branches"
```

---

### Task 2: legacy.py — finder delegates (xpath, xpaths, css, get_elements)

**Files:**
- Modify: `tests/test_legacy.py`

**Interfaces:**
- Consumes: `LegacyBrowser.xpath/xpaths/css/get_elements` (src/jc_selenium_helper/legacy.py:40-54), `Browser.find`/`Browser.find_all` (src/jc_selenium_helper/browser.py:35-39).
- Produces: nothing new for later tasks.

- [ ] **Step 1: Add the 4 finder delegate tests**

Append to `tests/test_legacy.py`:

```python
def test_legacy_xpath_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("basic.html"))
    with pytest.warns(DeprecationWarning):
        el = legacy.xpath("//h1[@id='title']")
    assert el.text == "Hello"


def test_legacy_xpaths_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("basic.html"))
    with pytest.warns(DeprecationWarning):
        els = legacy.xpaths("//li[@class='item']")
    assert len(els) == 3


def test_legacy_css_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("basic.html"))
    with pytest.warns(DeprecationWarning):
        el = legacy.css("#title")
    assert el.text == "Hello"


def test_legacy_get_elements_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("basic.html"))
    with pytest.warns(DeprecationWarning):
        els = legacy.get_elements("//li[@class='item']")
    assert len(els) == 3
```

- [ ] **Step 2: Run the new tests**

Run: `python -m pytest tests/test_legacy.py -k "xpath or css or get_elements" -v`
Expected: 4 new tests PASS.

- [ ] **Step 3: Confirm coverage moved**

Run: `python -m coverage run -m pytest -q && python -m coverage report -m`
Expected: `src/jc_selenium_helper/legacy.py` Missing list no longer includes `41-42, 45-46, 49-50, 53-54`.

- [ ] **Step 4: Commit**

```bash
git add tests/test_legacy.py
git commit -m "test: cover legacy xpath/xpaths/css/get_elements delegates"
```

---

### Task 3: legacy.py — wait delegates (wait_element_present, wait_element_not_present, wait_element_clickable, inhalt_geladen)

**Files:**
- Modify: `tests/test_legacy.py`

**Interfaces:**
- Consumes: `LegacyBrowser.wait_element_present/wait_element_not_present/wait_element_clickable/inhalt_geladen` (src/jc_selenium_helper/legacy.py:60-74), `Browser.wait_present/wait_not_present/wait_clickable/wait_document_ready` (src/jc_selenium_helper/browser.py:52-75).
- Produces: nothing new for later tasks.

- [ ] **Step 1: Add the 4 wait delegate tests**

Append to `tests/test_legacy.py`:

```python
def test_legacy_wait_element_present_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("basic.html"))
    with pytest.warns(DeprecationWarning):
        el = legacy.wait_element_present("//span[@id='late']")
    assert el.text == "here"


def test_legacy_wait_element_not_present_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("dynamic.html"))
    with pytest.warns(DeprecationWarning):
        result = legacy.wait_element_not_present("//div[@id='vanishing']")
    assert result is True


def test_legacy_wait_element_clickable_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("basic.html"))
    with pytest.warns(DeprecationWarning):
        el = legacy.wait_element_clickable("//button[@id='btn']")
    assert el.tag_name == "button"


def test_legacy_inhalt_geladen_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("basic.html"))
    with pytest.warns(DeprecationWarning):
        legacy.inhalt_geladen()
```

- [ ] **Step 2: Run the new tests**

Run: `python -m pytest tests/test_legacy.py -k "wait_element or inhalt_geladen" -v`
Expected: 4 new tests PASS.

- [ ] **Step 3: Confirm coverage moved**

Run: `python -m coverage run -m pytest -q && python -m coverage report -m`
Expected: `src/jc_selenium_helper/legacy.py` Missing list no longer includes `61-62, 65-66, 69-70, 73-74`.

- [ ] **Step 4: Commit**

```bash
git add tests/test_legacy.py
git commit -m "test: cover legacy wait_element_present/not_present/clickable and inhalt_geladen delegates"
```

---

### Task 4: legacy.py — mouse/tab/upload delegates

**Files:**
- Modify: `tests/test_legacy.py` (also add `from pathlib import Path` and `from selenium.webdriver.common.by import By` to its imports)

**Interfaces:**
- Consumes: `LegacyBrowser.doppelclick_element/hover_element/hover_element_with_offset/move_to_element/wait_move_click_element/click_new_tab/eingabe_upload_css` (src/jc_selenium_helper/legacy.py:76-106), `Browser.double_click/hover/hover_with_offset/move_to/wait_move_click/click_in_new_tab/upload_file` (src/jc_selenium_helper/browser.py:102-146).
- Produces: `Path` and `By` become available as imports in `tests/test_legacy.py` for any later use.

- [ ] **Step 1: Add `Path` and `By` imports**

At the top of `tests/test_legacy.py`, change:

```python
# tests/test_legacy.py
import pytest

from jc_selenium_helper.legacy import Browser as LegacyBrowser
```

to:

```python
# tests/test_legacy.py
from pathlib import Path

import pytest
from selenium.webdriver.common.by import By

from jc_selenium_helper.legacy import Browser as LegacyBrowser
```

- [ ] **Step 2: Add the 7 action delegate tests**

Append to `tests/test_legacy.py`:

```python
def test_legacy_doppelclick_element_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("basic.html"))
    with pytest.warns(DeprecationWarning):
        legacy.doppelclick_element(0, "//button[@id='dbl']")
    assert legacy.find("//button[@id='dbl']").text == "double"


def test_legacy_hover_element_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("dynamic.html"))
    with pytest.warns(DeprecationWarning):
        legacy.hover_element("//div[@id='hover-target']")
    assert legacy.find("//div[@id='hover-result']").text == "hovered"


def test_legacy_hover_element_with_offset_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("offset.html"))
    with pytest.warns(DeprecationWarning):
        legacy.hover_element_with_offset("//div[@id='anchor']", 100, 0)
    assert legacy.find("//div[@id='offset-result']").text == "offset-hovered"


def test_legacy_move_to_element_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("dynamic.html"))
    with pytest.warns(DeprecationWarning):
        legacy.move_to_element("//div[@id='hover-target']")
    assert legacy.find("//div[@id='hover-result']").text == "hovered"


def test_legacy_wait_move_click_element_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("basic.html"))
    with pytest.warns(DeprecationWarning):
        legacy.wait_move_click_element("//button[@id='clickable']")
    assert legacy.find("//button[@id='clickable']").text == "clicked"


def test_legacy_click_new_tab_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("basic.html"))
    with pytest.warns(DeprecationWarning):
        legacy.click_new_tab("//a[@id='newtab']", "//p[@id='target']")
    assert len(legacy.driver.window_handles) == 1
    assert legacy.find("//h1[@id='title']").text == "Hello"


def test_legacy_eingabe_upload_css_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("dynamic.html"))
    upload_path = str(Path(__file__).parent / "fixtures" / "basic.html")
    with pytest.warns(DeprecationWarning):
        legacy.eingabe_upload_css("#upload", upload_path)
    value = legacy.find("#upload", by=By.CSS_SELECTOR).get_attribute("value")
    assert value.endswith("basic.html")
```

- [ ] **Step 3: Run the new tests**

Run: `python -m pytest tests/test_legacy.py -k "doppelclick or hover_element or move_to_element or wait_move_click_element or click_new_tab or eingabe_upload_css" -v`
Expected: 7 new tests PASS.

- [ ] **Step 4: Confirm coverage moved**

Run: `python -m coverage run -m pytest -q && python -m coverage report -m`
Expected: `src/jc_selenium_helper/legacy.py` Missing list no longer includes `77-78, 81-82, 85-86, 89-90, 93-94, 97-98, 105-106`.

- [ ] **Step 5: Commit**

```bash
git add tests/test_legacy.py
git commit -m "test: cover legacy mouse/tab/upload delegates"
```

---

### Task 5: legacy.py — assertion delegates

**Files:**
- Modify: `tests/test_legacy.py`

**Interfaces:**
- Consumes: `LegacyBrowser.assert_checkbox_is_checked/assert_checkbox_is_not_checked/check_select/ele_test` (src/jc_selenium_helper/legacy.py:108-122), `Browser.assert_checkbox_checked/assert_checkbox_unchecked/assert_selected_option/assert_present` (src/jc_selenium_helper/browser.py:149-169).
- Produces: nothing new for later tasks.

- [ ] **Step 1: Add the 4 assertion delegate tests**

Append to `tests/test_legacy.py`:

```python
def test_legacy_assert_checkbox_is_checked_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("basic.html"))
    with pytest.warns(DeprecationWarning):
        legacy.assert_checkbox_is_checked("//input[@id='checked-box']")


def test_legacy_assert_checkbox_is_not_checked_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("basic.html"))
    with pytest.warns(DeprecationWarning):
        legacy.assert_checkbox_is_not_checked("//input[@id='unchecked-box']")


def test_legacy_check_select_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("basic.html"))
    with pytest.warns(DeprecationWarning):
        legacy.check_select("//select[@id='picker']", "two")


def test_legacy_ele_test_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("basic.html"))
    with pytest.warns(DeprecationWarning):
        legacy.ele_test("//h1[@id='title']")
```

- [ ] **Step 2: Run the new tests**

Run: `python -m pytest tests/test_legacy.py -k "assert_checkbox_is or check_select or ele_test" -v`
Expected: 4 new tests PASS.

- [ ] **Step 3: Confirm coverage moved**

Run: `python -m coverage run -m pytest -q && python -m coverage report -m`
Expected: `src/jc_selenium_helper/legacy.py` Missing list no longer includes `109-110, 113-114, 117-118, 121-122`.

- [ ] **Step 4: Commit**

```bash
git add tests/test_legacy.py
git commit -m "test: cover legacy checkbox/select/present assertion delegates"
```

---

### Task 6: legacy.py — seite_geladen success path

**Files:**
- Modify: `tests/test_legacy.py`

**Interfaces:**
- Consumes: `LegacyBrowser.seite_geladen(check_path: str) -> None` (src/jc_selenium_helper/legacy.py:130-143), which internally calls `self.inhalt_geladen()`.
- Produces: nothing new for later tasks.

- [ ] **Step 1: Add the seite_geladen success-path test**

Append to `tests/test_legacy.py`:

```python
def test_legacy_seite_geladen_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("basic.html"))
    with pytest.warns(DeprecationWarning):
        legacy.seite_geladen("//h1[@id='title']")
```

Note: this exercises only the success path (element present on the first
check, no refresh). The failure path — refreshing up to 5 times with a
hardcoded `sleep(10)` between attempts — is intentionally not tested; it
would add 50+ seconds to the suite for one already-understood `ValueError`
branch (documented as a non-goal in the design spec).

- [ ] **Step 2: Run the new test**

Run: `python -m pytest tests/test_legacy.py -k seite_geladen -v`
Expected: 1 new test PASSes (takes ~1s due to the method's internal `sleep(1)`).

- [ ] **Step 3: Confirm coverage moved**

Run: `python -m coverage run -m pytest -q && python -m coverage report -m`
Expected: `src/jc_selenium_helper/legacy.py` Missing list no longer includes `131-143`.

- [ ] **Step 4: Commit**

```bash
git add tests/test_legacy.py
git commit -m "test: cover legacy seite_geladen success path"
```

---

### Task 7: Final verification

**Files:** none (verification only)

**Interfaces:**
- Consumes: the full test suite and coverage configuration from all prior tasks.
- Produces: final confirmation that the plan's goal is met.

- [ ] **Step 1: Run the full suite with coverage**

Run: `python -m coverage run -m pytest -q && python -m coverage report -m`
Expected: all tests PASS; `src/jc_selenium_helper/legacy.py` and `src/jc_selenium_helper/browser.py` both show `100%` (no `Missing` column entries); `TOTAL` is in the high 90s (roughly 97-99%, per the design spec's estimate); exit code 0 (the `fail_under = 80` gate passes with margin).

- [ ] **Step 2: Run lint**

Run: `ruff check .`
Expected: no errors (new imports in `tests/test_legacy.py` — `Path`, `By` — must actually be used, which they are, starting Task 4).

- [ ] **Step 3: Confirm nothing else changed**

Run: `git status` and `git diff --stat master` (or the relevant base branch)
Expected: only `tests/test_legacy.py`, `tests/test_browser_waits.py`, and `tests/test_browser_actions.py` are modified; no production source files touched, matching the design spec's non-goals.
