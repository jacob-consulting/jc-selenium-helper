# Colors

Small helper module that replaces the old `colormap`/`easydev` dependency for
converting a CSS color string (as read back from a computed style) into a hex
string.

### `rgb_to_hex(rgb_string: str) -> str`

Converts a CSS `rgb(...)` or `rgba(...)` string to `#rrggbb`. The alpha channel
of `rgba` is ignored.

```python
from jc_selenium_helper.colors import rgb_to_hex

rgb_to_hex("rgb(255, 0, 0)")        # "#ff0000"
rgb_to_hex("rgba(0, 128, 255, 0.5)")  # "#0080ff"
```

A common use case is asserting on an element's computed color:

```python
color = browser.find("//div[@id='badge']").value_of_css_property("color")
assert rgb_to_hex(color) == "#ff0000"
```
