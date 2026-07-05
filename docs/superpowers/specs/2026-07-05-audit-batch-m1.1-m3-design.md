# Audit batch — M1.1 + M3.1 + M3.3 + M3.4

**Date:** 2026-07-05
**Status:** Design approved, pending implementation plan
**Audit ref:** `docs/superpowers/notes/2026-07-04-audit.md` — closes M1.1 (correctness) and the
M3 polish items M3.1, M3.3, M3.4. M2.1 (coverage floor) is deliberately **out of scope**
(it needs the plugin-import coverage-measurement fix + a floor-% decision, a separate pass).

Four small, independent changes, bundled because each is S effort and low-risk.

---

## 1. M1.1 — Delete `legacy.switch_and_fill_frame`

**Decision (owner-approved):** delete, not re-signature.

`switch_and_fill_frame(self, combined, path, text)` (`src/jc_selenium_helper/legacy.py`) is
**unrunnable** — it calls `time.sleep(combined.settings.k_pause)` on a `combined` object with
no source in this package, and hardcodes the TinyMCE inner path `//*[@id='tinymce']/p`. No
working caller can exist. The generic replacement `fill_in_frame(frame_path, inner_path, text)`
already exists and the migration guide already maps to it.

**Changes:**
- Remove the `switch_and_fill_frame` method from `LegacyBrowser`. Also remove the now-unused
  `Keys` import from `legacy.py` if `switch_and_fill_frame` was its only user (verify: it is —
  `seite_geladen` does not use `Keys`).
- `seite_geladen` stays untouched.
- `docs/reference/migration.md`: change the `switch_and_fill_frame` mapping row and the
  verbatim-behavior bullet to state it was **removed**; direct callers to
  `fill_in_frame(frame_path, inner_path, text)`, passing their own pause explicitly (e.g. a
  preceding `time.sleep`).

**Test** (`tests/test_legacy.py`): a regression guard that the method is gone.
```python
def test_switch_and_fill_frame_removed():
    assert not hasattr(LegacyBrowser, "switch_and_fill_frame")
```

## 2. M3.1 — Unify assertion wait semantics (`src/jc_selenium_helper/browser.py`)

Today `assert_checkbox_checked`/`assert_checkbox_unchecked` wait (`wait_present`), but
`assert_present` and `assert_selected_option` resolve immediately, so a slightly-late element
flakes the latter two. Add an optional `timeout` and wait for presence, matching the checkbox
asserts.

**`assert_present`** — presence *is* the assertion, so convert a wait timeout to `AssertionError`:
```python
def assert_present(self, locator: str, by: str = By.XPATH, timeout: float | None = None) -> None:
    try:
        self.wait_present(locator, by, timeout)
    except TimeoutException:
        raise AssertionError(f"Element not present: {locator}") from None
```

**`assert_selected_option`** — resolve the `<select>` via `wait_present` (so a late-appearing
select is waited for), then compare. An absent element surfaces as `TimeoutException`, exactly
matching the existing `assert_checkbox_checked` pattern (deliberate: only `assert_present`
converts, because presence is its whole contract):
```python
def assert_selected_option(self, locator: str, expected_text: str, by: str = By.XPATH,
                           timeout: float | None = None) -> None:
    select = Select(self.wait_present(locator, by, timeout))
    actual = select.first_selected_option.text
    if actual != expected_text:
        raise AssertionError(f"Selected option '{actual}' != expected '{expected_text}'")
```

`TimeoutException` and `Select` are already imported in `browser.py`. `wait_present` already
has signature `(locator, by=By.XPATH, timeout=None) -> WebElement`.

**Fixture** (`tests/fixtures/dynamic.html`): extend the existing `<script>` (which already has a
`setTimeout` for `#vanishing`) to *append* two late elements after a short delay — a
`<div id="late-element">` and a `<select id="late-select">` whose second option is `selected`
(text `two`). Additive; does not disturb existing `#vanishing`/`#hover-target`/`#upload` tests.

**Tests** (`tests/test_browser_assertions.py`), each proving the wait (would fail immediately
without it), using the existing `browser` fixture (`default_timeout=10`, `poll_pause=0.2`):
```python
def test_assert_present_waits_for_late_element(browser, fixture_url):
    browser.open(fixture_url("dynamic.html"))
    browser.assert_present("//div[@id='late-element']")

def test_assert_selected_option_waits_for_late_select(browser, fixture_url):
    browser.open(fixture_url("dynamic.html"))
    browser.assert_selected_option("//select[@id='late-select']", "two")
```
Existing assertion tests (`basic.html`, immediate elements) remain green unchanged.

## 3. M3.3 — Validate `rgb_to_hex` input (`src/jc_selenium_helper/colors.py`)

Today malformed input raises a bare `ValueError`/`IndexError` from `str.index`/`int(float(...))`.
Add explicit validation with a message echoing the offending input:
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
        raise ValueError(f"rgb() needs at least 3 components, got {len(components)}: {rgb_string!r}")
    try:
        r, g, b = (int(float(c.strip())) for c in components[:3])
    except ValueError:
        raise ValueError(f"Non-numeric rgb component in {rgb_string!r}") from None
    return f"#{r:02x}{g:02x}{b:02x}"
```

**Tests** (`tests/test_colors.py`): keep the existing valid-conversion parametrize; add a
parametrized malformed case asserting `pytest.raises(ValueError)` for at least: a string with no
parens (`"not a color"`), too few components (`"rgb(1, 2)"`), and a non-numeric component
(`"rgb(a, b, c)"`).

## 4. M3.4 — Pin ruff consistently

`ruff` is unpinned in the `dev`/`test` extras while `.pre-commit-config.yaml` pins `rev: v0.8.0`
(large drift; local ruff is 0.15.20).

**Decision (owner-approved):** compatible-release, not exact pin.
- `pyproject.toml` `dev` and `test` extras: `ruff~=0.15.0` (tracks the 0.15.x line).
- `.pre-commit-config.yaml`: `rev: v0.15.20` (a specific tag within that line).

Both reference the same 0.15.x series. Config-only; no source change. Because the pre-commit
version jumps 0.8→0.15, re-run `ruff format` and `ruff check` on the tree afterward and commit
any resulting reformat so CI/pre-commit agree.

---

## Testing / verification

- Full suite green: `.venv/bin/pytest -q` (existing 50 + new: 1 legacy-removal, 2 assertion
  late-appearance, ~1 added malformed-colors param case).
- `.venv/bin/ruff check .` and `.venv/bin/ruff format --check .` clean under the newly pinned
  ruff.

## CHANGELOG (`CHANGELOG.md`, existing `## Unreleased` section)

Fold new entries into the existing `## Unreleased` block — no version bump:
- **Removed** — `legacy.switch_and_fill_frame` (was unrunnable; use `fill_in_frame`).
- **Changed** — `assert_present` and `assert_selected_option` now wait for the element (new
  optional `timeout`), consistent with the checkbox asserts.
- **Fixed** — `rgb_to_hex` raises a clear `ValueError` on malformed input.
- **Internal** — pinned ruff to the 0.15.x line across extras and pre-commit.

## Acceptance criteria

- `switch_and_fill_frame` no longer exists on `LegacyBrowser`; migration doc updated; guard test passes.
- `assert_present`/`assert_selected_option` accept `timeout` and wait; late-appearance tests pass.
- `rgb_to_hex` raises descriptive `ValueError` on the three malformed shapes; valid conversions unchanged.
- Extras and pre-commit both reference ruff 0.15.x; `ruff check`/`format --check` clean.
- Full suite green; no version bump; M2.1 untouched.

## Open questions

None — M1.1 (delete), M3.1 (add waiting; `assert_selected_option` absent→`TimeoutException`),
and M3.4 (`~=0.15.0`) are all resolved.
