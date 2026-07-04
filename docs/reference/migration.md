# Migration from the legacy API

Existing suites written against the original app-specific, German-named
`libs.browser.Browser` can migrate with a one-line import swap:

```python
# before
from libs.browser import Browser

# after
from jc_selenium_helper.legacy import Browser
```

`jc_selenium_helper.legacy.Browser` (an alias for `LegacyBrowser`) is a subclass
of the clean `jc_selenium_helper.browser.Browser`. Every legacy method emits a
`DeprecationWarning` naming its replacement and delegates to the new API, so
existing test suites keep working unchanged while you migrate call sites at
your own pace.

Two methods keep their original, app-specific behavior verbatim instead of
delegating to a generic equivalent, because they encode assumptions the
generic replacement deliberately drops:

- `seite_geladen` hardcoded a fixed 1-second initial sleep and a
  `ValueError("Seite nicht geladen")` on giving up; `wait_page_loaded` raises
  `TimeoutError` instead and takes `retries`/`interval` as parameters.
- `switch_and_fill_frame` hardcoded a TinyMCE-specific inner path
  (`//*[@id='tinymce']/p`) and a project settings object
  (`combined.settings.k_pause`); `fill_in_frame` takes the inner path as a
  parameter and has no dependency on project settings.

## Method mapping

| Legacy name (German/ad-hoc) | New equivalent |
| --- | --- |
| `xpath` | `find` |
| `xpaths` | `find_all` |
| `css` | `find` (with `by=By.CSS_SELECTOR`) |
| `get_elements` | `find_all` |
| `check_exists_by_xpath` | `exists` |
| `wait_element_present` | `wait_present` |
| `wait_element_not_present` | `wait_not_present` |
| `wait_element_clickable` | `wait_clickable` |
| `inhalt_geladen` | `wait_document_ready` |
| `seite_geladen` | `wait_page_loaded` |
| `doppelclick_element` | `double_click` |
| `hover_element` | `hover` |
| `hover_element_with_offset` | `hover_with_offset` |
| `move_to_element` | `move_to` |
| `wait_move_click_element` | `wait_move_click` |
| `click_new_tab` | `click_in_new_tab` |
| `eingabe` | `type_text` |
| `eingabe_upload_css` | `upload_file` |
| `assert_checkbox_is_checked` | `assert_checkbox_checked` |
| `assert_checkbox_is_not_checked` | `assert_checkbox_unchecked` |
| `check_select` | `assert_selected_option` |
| `ele_test` | `assert_present` |
| `switch_rgb` | `jc_selenium_helper.colors.rgb_to_hex` |
| `switch_and_fill_frame` | `fill_in_frame` |

See [Browser](browser.md) for the full signatures of the new methods and
[Colors](colors.md) for `rgb_to_hex`.
