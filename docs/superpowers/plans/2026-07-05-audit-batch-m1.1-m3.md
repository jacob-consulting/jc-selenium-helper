# Audit Batch M1.1 + M3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close audit items M1.1 (delete the unrunnable `legacy.switch_and_fill_frame`), M3.1 (make `assert_present`/`assert_selected_option` wait like the checkbox asserts), M3.3 (`rgb_to_hex` input validation), and M3.4 (pin ruff consistently).

**Architecture:** Four independent, low-risk changes to existing modules, each with its own TDD test cycle, plus a final CHANGELOG + whole-suite verification task. No new files except none — all edits land in existing source, fixtures, tests, and config.

**Tech Stack:** Python 3.12+, Selenium 4.38+ (`ActionChains`, `Select`, `WebDriverWait`), pytest + pytest-selenium, ruff.

## Global Constraints

- `requires-python >= 3.12`; supported matrix 3.12 / 3.13 / 3.14 — keep code compatible with all three.
- Runtime dependency is `selenium>=4.38` only; no new dependencies.
- Locators default to XPath (`by=By.XPATH`); pass `by=By.CSS_SELECTOR` for CSS. `Browser.__init__(self, driver, default_timeout=120, poll_pause=1)` stores the driver as `self.driver`. The `browser` test fixture uses `default_timeout=10`, `poll_pause=0.2`.
- Tests assert real observable behavior, not just "does not raise". HTML fixtures live in `tests/fixtures/`.
- Run tests with `.venv/bin/pytest` and linters with `.venv/bin/ruff` (venv is uv-managed).
- NO release / version bump. CHANGELOG changes fold into the existing `## Unreleased` section only.
- `seite_geladen` (the other "verbatim" legacy method) must stay untouched.
- Reference spec: `docs/superpowers/specs/2026-07-05-audit-batch-m1.1-m3-design.md`.

---

### Task 1: M1.1 — Delete `legacy.switch_and_fill_frame`

**Files:**
- Modify: `src/jc_selenium_helper/legacy.py` (remove method ~lines 146-154; remove `Keys` import at line 24)
- Modify: `docs/reference/migration.md` (the `switch_and_fill_frame` mapping row + its verbatim-behavior bullet)
- Test: `tests/test_legacy.py` (add one guard test)

**Interfaces:**
- Consumes: `from jc_selenium_helper.legacy import Browser as LegacyBrowser` (already imported at the top of `tests/test_legacy.py`).
- Produces: `LegacyBrowser` no longer has a `switch_and_fill_frame` attribute.

- [ ] **Step 1: Write the failing guard test**

Add to `tests/test_legacy.py`:

```python
def test_switch_and_fill_frame_removed():
    # M1.1: the unrunnable legacy method was deleted; callers use fill_in_frame.
    assert not hasattr(LegacyBrowser, "switch_and_fill_frame")
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `.venv/bin/pytest tests/test_legacy.py::test_switch_and_fill_frame_removed -v`
Expected: FAIL — the method still exists, so `hasattr` is `True`.

- [ ] **Step 3: Delete the method**

In `src/jc_selenium_helper/legacy.py`, remove the entire `switch_and_fill_frame` method (the block starting `def switch_and_fill_frame(self, combined, path, text):` through its final `self.driver.switch_to.default_content()` line). Leave `seite_geladen` and the `# -- verbatim app-specific behavior ...` comment's other content intact. The current block to delete:

```python
    def switch_and_fill_frame(self, combined, path, text):
        _deprecated("switch_and_fill_frame", "fill_in_frame")
        time.sleep(combined.settings.k_pause)
        switch_frame = self.driver.find_element(By.XPATH, path)
        self.driver.switch_to.frame(switch_frame)
        tmp_path = "//*[@id='tinymce']/p"
        self.type_text(tmp_path, text)
        self.type_text(tmp_path, Keys.RETURN)
        self.driver.switch_to.default_content()
```

- [ ] **Step 4: Remove the now-unused `Keys` import**

`Keys` was used only by the deleted method. In `src/jc_selenium_helper/legacy.py` remove the line:

```python
from selenium.webdriver.common.keys import Keys
```

(Leave `import time` — `seite_geladen` still uses `time.sleep`. Leave the `By` import — other methods use it.)

- [ ] **Step 5: Run the guard test and lint to verify**

Run: `.venv/bin/pytest tests/test_legacy.py::test_switch_and_fill_frame_removed -v`
Expected: PASS.
Run: `.venv/bin/ruff check src/jc_selenium_helper/legacy.py`
Expected: no errors (confirms no unused-import `F401` from the dropped `Keys`).

- [ ] **Step 6: Update the migration guide**

In `docs/reference/migration.md`:

Replace the `switch_and_fill_frame` verbatim-behavior bullet:

```markdown
- `switch_and_fill_frame` hardcoded a TinyMCE-specific inner path
  (`//*[@id='tinymce']/p`) and a project settings object
  (`combined.settings.k_pause`); `fill_in_frame` takes the inner path as a
  parameter and has no dependency on project settings.
```

with:

```markdown
- `switch_and_fill_frame` was **removed** (it was unrunnable outside its
  original app — it depended on a `combined.settings.k_pause` object that does
  not exist in this package, and hardcoded the TinyMCE inner path
  `//*[@id='tinymce']/p`). Use `fill_in_frame(frame_path, inner_path, text)`
  instead, passing the inner path explicitly and adding your own `time.sleep`
  beforehand if you need the old pause.
```

And change the mapping-table row:

```markdown
| `switch_and_fill_frame` | `fill_in_frame` |
```

to:

```markdown
| `switch_and_fill_frame` | **removed** — use `fill_in_frame` |
```

- [ ] **Step 7: Commit**

```bash
git add src/jc_selenium_helper/legacy.py tests/test_legacy.py docs/reference/migration.md
git commit -m "refactor!: remove unrunnable legacy.switch_and_fill_frame (M1.1)"
```

---

### Task 2: M3.1 — Unify assertion wait semantics

**Files:**
- Modify: `src/jc_selenium_helper/browser.py` (`assert_selected_option` and `assert_present`, ~lines 159-167)
- Modify: `tests/fixtures/dynamic.html` (append two late elements)
- Test: `tests/test_browser_assertions.py` (add two tests)

**Interfaces:**
- Consumes: `self.wait_present(locator, by=By.XPATH, timeout=None) -> WebElement` (existing); `Select` and `TimeoutException` are already imported in `browser.py`.
- Produces:
  - `assert_present(self, locator: str, by: str = By.XPATH, timeout: float | None = None) -> None`
  - `assert_selected_option(self, locator: str, expected_text: str, by: str = By.XPATH, timeout: float | None = None) -> None`

- [ ] **Step 1: Add late-appearing elements to the fixture**

Replace the entire contents of `tests/fixtures/dynamic.html` with (adds a second `setTimeout` that appends `#late-element` and `#late-select`; everything else is unchanged):

```html
<!-- tests/fixtures/dynamic.html -->
<!doctype html>
<html>
  <head><title>dynamic</title></head>
  <body>
    <div id="vanishing">now you see me</div>
    <div id="hover-target">hover me</div>
    <div id="hover-result"></div>
    <input id="upload" type="file" />
    <script>
      // #vanishing disappears shortly after load
      setTimeout(function () {
        document.getElementById("vanishing").style.display = "none";
      }, 300);
      // record the first hover onto #hover-target
      document
        .getElementById("hover-target")
        .addEventListener("mouseover", function () {
          document.getElementById("hover-result").textContent = "hovered";
        });
      // append late elements to exercise the assertion waits (M3.1)
      setTimeout(function () {
        var late = document.createElement("div");
        late.id = "late-element";
        late.textContent = "late";
        document.body.appendChild(late);

        var select = document.createElement("select");
        select.id = "late-select";
        select.innerHTML =
          '<option value="one">one</option>' +
          '<option value="two" selected>two</option>';
        document.body.appendChild(select);
      }, 300);
    </script>
  </body>
</html>
```

- [ ] **Step 2: Write the failing tests**

Add to `tests/test_browser_assertions.py`:

```python
def test_assert_present_waits_for_late_element(browser, fixture_url):
    browser.open(fixture_url("dynamic.html"))
    # #late-element is appended ~300ms after load; the assertion must wait.
    browser.assert_present("//div[@id='late-element']")


def test_assert_selected_option_waits_for_late_select(browser, fixture_url):
    browser.open(fixture_url("dynamic.html"))
    # #late-select is appended ~300ms after load; the assertion must wait.
    browser.assert_selected_option("//select[@id='late-select']", "two")
```

Also update the existing `test_assert_present_fails_when_missing` — now that `assert_present` waits, a missing element would otherwise poll for the full `default_timeout` (10s). Pass a short timeout so it fails fast. Replace:

```python
def test_assert_present_fails_when_missing(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    with pytest.raises(AssertionError):
        browser.assert_present("//div[@id='nope']")
```

with:

```python
def test_assert_present_fails_when_missing(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    with pytest.raises(AssertionError):
        browser.assert_present("//div[@id='nope']", timeout=0.5)
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `.venv/bin/pytest tests/test_browser_assertions.py::test_assert_present_waits_for_late_element tests/test_browser_assertions.py::test_assert_selected_option_waits_for_late_select -v`
Expected: FAIL — `assert_present` currently checks `exists()` immediately and raises `AssertionError`; `assert_selected_option` currently calls `find()` immediately and raises `NoSuchElementException`. Both fire before the element is appended. (Note: `test_assert_present_fails_when_missing` will error at collection/call because the current `assert_present` has no `timeout` parameter — expected; Step 4 adds it.)

- [ ] **Step 4: Implement the waiting versions**

In `src/jc_selenium_helper/browser.py`, replace:

```python
    def assert_selected_option(self, locator: str, expected_text: str, by: str = By.XPATH) -> None:
        select = Select(self.find(locator, by))
        actual = select.first_selected_option.text
        if actual != expected_text:
            raise AssertionError(f"Selected option '{actual}' != expected '{expected_text}'")

    def assert_present(self, locator: str, by: str = By.XPATH) -> None:
        if not self.exists(locator, by):
            raise AssertionError(f"Element not present: {locator}")
```

with:

```python
    def assert_selected_option(
        self, locator: str, expected_text: str, by: str = By.XPATH, timeout: float | None = None
    ) -> None:
        select = Select(self.wait_present(locator, by, timeout))
        actual = select.first_selected_option.text
        if actual != expected_text:
            raise AssertionError(f"Selected option '{actual}' != expected '{expected_text}'")

    def assert_present(self, locator: str, by: str = By.XPATH, timeout: float | None = None) -> None:
        try:
            self.wait_present(locator, by, timeout)
        except TimeoutException:
            raise AssertionError(f"Element not present: {locator}") from None
```

- [ ] **Step 5: Run the new tests and the existing assertion tests**

Run: `.venv/bin/pytest tests/test_browser_assertions.py -v`
Expected: PASS — the two new tests pass, and every pre-existing assertion test still passes, including `test_assert_present_fails_when_missing`, which now raises `AssertionError` after its short `timeout=0.5` elapses (fast, no 10s hang).

- [ ] **Step 6: Lint**

Run: `.venv/bin/ruff check src/jc_selenium_helper/browser.py && .venv/bin/ruff format --check src/jc_selenium_helper/browser.py`
Expected: no errors.

- [ ] **Step 7: Commit**

```bash
git add src/jc_selenium_helper/browser.py tests/fixtures/dynamic.html tests/test_browser_assertions.py
git commit -m "feat: assert_present/assert_selected_option wait for the element (M3.1)"
```

---

### Task 3: M3.3 — Validate `rgb_to_hex` input

**Files:**
- Modify: `src/jc_selenium_helper/colors.py` (`rgb_to_hex`)
- Test: `tests/test_colors.py` (add malformed-input tests)

**Interfaces:**
- Produces: `rgb_to_hex(rgb_string: str) -> str` — unchanged signature; now raises `ValueError` with a message containing the offending input on malformed strings.

- [ ] **Step 1: Write the failing tests**

The improvement is a *descriptive* error whose message echoes the offending input. Add to `tests/test_colors.py` (the module already imports `pytest` and `rgb_to_hex`):

```python
@pytest.mark.parametrize(
    "value",
    [
        "not a color",     # no parentheses
        "rgb(1, 2)",       # too few components
        "rgb(a, b, c)",    # non-numeric components
    ],
)
def test_rgb_to_hex_rejects_malformed(value):
    with pytest.raises(ValueError, match=re.escape(value)):
        rgb_to_hex(value)
```

Add `import re` to the top of `tests/test_colors.py` (above `import pytest`).

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/pytest tests/test_colors.py::test_rgb_to_hex_rejects_malformed -v`
Expected: FAIL — the current code raises `ValueError`/`IndexError`, but with bare messages ("substring not found", "not enough values to unpack", "could not convert string to float: 'a'") that do NOT contain the full offending input string, so `match=re.escape(value)` fails.

- [ ] **Step 3: Implement validation**

Replace the body of `rgb_to_hex` in `src/jc_selenium_helper/colors.py`:

```python
def rgb_to_hex(rgb_string: str) -> str:
    """Convert a CSS ``rgb(...)`` or ``rgba(...)`` string to ``#rrggbb``.

    The alpha channel of ``rgba`` is ignored. Raises ``ValueError`` with a
    descriptive message if the string is not a valid ``rgb()``/``rgba()`` form.
    """
    if "(" not in rgb_string or ")" not in rgb_string:
        raise ValueError(f"Not an rgb()/rgba() string: {rgb_string!r}")
    inner = rgb_string[rgb_string.index("(") + 1 : rgb_string.index(")")]
    components = inner.split(",")
    if len(components) < 3:
        raise ValueError(
            f"rgb() needs at least 3 components, got {len(components)}: {rgb_string!r}"
        )
    try:
        r, g, b = (int(float(component.strip())) for component in components[:3])
    except ValueError:
        raise ValueError(f"Non-numeric rgb component in {rgb_string!r}") from None
    return f"#{r:02x}{g:02x}{b:02x}"
```

Note: `{rgb_string!r}` renders `'not a color'`, `'rgb(1, 2)'`, `'rgb(a, b, c)'` — the `re.escape(value)` match finds the value inside the quoted repr.

- [ ] **Step 4: Run the colors tests**

Run: `.venv/bin/pytest tests/test_colors.py -v`
Expected: PASS — the existing valid-conversion parametrize (`test_rgb_to_hex`) still passes, and the three malformed cases now raise a `ValueError` whose message contains the input.

- [ ] **Step 5: Lint**

Run: `.venv/bin/ruff check src/jc_selenium_helper/colors.py tests/test_colors.py && .venv/bin/ruff format --check src/jc_selenium_helper/colors.py tests/test_colors.py`
Expected: no errors.

- [ ] **Step 6: Commit**

```bash
git add src/jc_selenium_helper/colors.py tests/test_colors.py
git commit -m "fix: rgb_to_hex raises a descriptive ValueError on malformed input (M3.3)"
```

---

### Task 4: M3.4 — Pin ruff consistently

**Files:**
- Modify: `pyproject.toml` (`dev` and `test` extras)
- Modify: `.pre-commit-config.yaml` (ruff-pre-commit `rev`)

**Interfaces:**
- Produces: no code interface; both config sources reference ruff on the 0.15.x line.

- [ ] **Step 1: Pin ruff in the extras**

In `pyproject.toml`, find the two unpinned `ruff` entries (one in the `dev` extra, one in the `test` extra — each is a bare `"ruff",` line) and change each to:

```toml
    "ruff~=0.15.0",
```

- [ ] **Step 2: Bump the pre-commit ruff rev**

In `.pre-commit-config.yaml`, change:

```yaml
    rev: v0.8.0
```

to:

```yaml
    rev: v0.15.20
```

- [ ] **Step 3: Re-format and lint the whole tree under the pinned ruff**

The local ruff is already 0.15.20, but run these to guarantee the tree is clean under the pinned version and commit any reformat:

Run: `.venv/bin/ruff format . && .venv/bin/ruff check .`
Expected: `ruff check` reports "All checks passed"; `ruff format` reports files already formatted (or reformats a few — that's fine, it will be committed).

- [ ] **Step 4: Verify the config is internally consistent**

Run: `grep -n "ruff" pyproject.toml .pre-commit-config.yaml`
Expected: both extras show `ruff~=0.15.0`; pre-commit shows `rev: v0.15.20`. No bare `"ruff",` remains.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml .pre-commit-config.yaml
git commit -m "build: pin ruff to the 0.15.x line across extras and pre-commit (M3.4)"
```

If Step 3 reformatted any source files, add them to this commit as well.

---

### Task 5: CHANGELOG + whole-suite verification

**Files:**
- Modify: `CHANGELOG.md` (existing `## Unreleased` section)

**Interfaces:**
- Consumes: nothing.
- Produces: nothing.

- [ ] **Step 1: Extend the Unreleased CHANGELOG section**

`CHANGELOG.md` already has a `## Unreleased` block (with `### Fixed` and `### Internal` from the prior batch). Update that block so it reads exactly:

```markdown
## Unreleased

### Removed

- `legacy.switch_and_fill_frame` — it was unrunnable outside its original app
  (it depended on a `combined.settings.k_pause` object absent from this package
  and hardcoded a TinyMCE inner path). Use `fill_in_frame(frame_path,
  inner_path, text)` instead.

### Changed

- `assert_present` and `assert_selected_option` now wait for the element (new
  optional `timeout` parameter), consistent with the checkbox asserts, instead
  of resolving immediately.

### Fixed

- `hover_with_offset` now applies the offset in a single chained `ActionChains`
  action (`move_to_element(...).move_by_offset(...)`) instead of two separate
  `perform()` calls. The observable pointer destination is unchanged; the
  implementation is simpler and its intent clearer.
- `rgb_to_hex` now raises a descriptive `ValueError` (naming the offending
  input) on malformed strings instead of a bare `ValueError`/`IndexError`.

### Internal

- Test backfill for the last two untested surfaces from the audit's M0.2:
  `hover_with_offset` (real headless-Chrome behavior via a new `offset.html`
  fixture) and the `jc_browser` plugin fixture (wiring verified under
  `pytester`). No API changes.
- Pinned ruff to the 0.15.x line across the `dev`/`test` extras and pre-commit.
```

(This preserves the prior batch's `hover_with_offset` Fixed entry and the M0.2 Internal entry, and adds the Removed/Changed entries plus the two new Fixed/Internal lines.)

- [ ] **Step 2: Run the full test suite**

Run: `.venv/bin/pytest -q`
Expected: all tests pass — prior 50 plus 1 (legacy guard) + 2 (assertion waits) + the new malformed-colors parametrize cases. No failures, no errors.

- [ ] **Step 3: Run the full linters under the pinned ruff**

Run: `.venv/bin/ruff check . && .venv/bin/ruff format --check .`
Expected: "All checks passed" and all files already formatted.

- [ ] **Step 4: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs(changelog): unreleased entries for M1.1 + M3.1/M3.3/M3.4"
```

---

## Notes for the implementer

- **Task order matters only slightly.** Tasks 1-4 touch disjoint files (`legacy.py`, `browser.py`+`dynamic.html`, `colors.py`, config). Task 5 depends on all of them (CHANGELOG summarizes them, and the full-suite run needs every prior test present). Do them in order.
- **Do not bump the package version.** All CHANGELOG entries go under the existing `## Unreleased` heading. Releasing is a separate step the owner triggers.
- **`assert_present` vs `assert_selected_option` timeout handling is deliberately asymmetric:** `assert_present` converts a `TimeoutException` to `AssertionError` (presence is its whole assertion); `assert_selected_option` lets an absent element surface as `TimeoutException`, matching the existing `assert_checkbox_checked` pattern. This is intentional — do not "fix" it to be uniform.
- **`seite_geladen` stays exactly as-is.** Only `switch_and_fill_frame` is removed in Task 1.
