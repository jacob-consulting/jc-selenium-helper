# Browser

`Browser` wraps a Selenium `WebDriver`. Locators default to XPath; pass
`by=By.CSS_SELECTOR` (or any Selenium `By` value) to use a different strategy.

```python
from jc_selenium_helper import Browser

browser = Browser(driver, default_timeout=120, poll_pause=1)
```

- `default_timeout` (`float`, default `120`) — seconds used by wait methods when
  no explicit `timeout` is given.
- `poll_pause` (`float`, default `1`) — seconds slept between polling attempts
  (`wait_document_ready`, `move_to`, `wait_move_click`).

## Navigation

### `open(url: str) -> None`

Loads `url` via `driver.get`.

```python
browser.open("https://example.com")
```

## Finders

### `find(locator: str, by: str = By.XPATH) -> WebElement`

Returns the first matching element, raising `NoSuchElementException` if absent.

```python
element = browser.find("//button[@type='submit']")
```

### `find_all(locator: str, by: str = By.XPATH) -> list[WebElement]`

Returns all matching elements (empty list if none).

```python
rows = browser.find_all("//table//tr")
```

### `exists(locator: str, by: str = By.XPATH) -> bool`

Returns `True`/`False` without raising.

```python
if browser.exists("//div[@class='error']"):
    ...
```

## Waits

Wait methods accept an optional `timeout` (falls back to `self.default_timeout`
when `None`).

### `wait_present(locator: str, by: str = By.XPATH, timeout: float | None = None) -> WebElement`

Waits until the element is present in the DOM, then returns it.

```python
browser.wait_present("//div[@id='content']", timeout=10)
```

### `wait_clickable(locator: str, by: str = By.XPATH, timeout: float | None = None) -> WebElement`

Waits until the element is clickable, then returns it.

```python
browser.wait_clickable("//button[@id='submit']")
```

### `wait_not_present(locator: str, by: str = By.XPATH, timeout: float | None = None) -> bool`

Waits until the element is invisible/absent. Raises `TimeoutException` (with a
message naming the locator and timeout) if it is still present after `timeout`.

```python
browser.wait_not_present("//div[@class='spinner']")
```

### `wait_document_ready(timeout: float | None = None) -> None`

Polls `document.readyState` every `poll_pause` seconds until it is `"complete"`.
Raises `TimeoutError` if it never completes within `timeout`.

```python
browser.wait_document_ready()
```

### `wait_page_loaded(check_path: str, by: str = By.XPATH, retries: int = 5, interval: float = 10) -> None`

Waits for `check_path` to appear, refreshing the page between attempts (up to
`retries` times, sleeping `interval` seconds between each), then waits for
`wait_document_ready`. Raises `TimeoutError` if `check_path` never appears.
Generic replacement for the app-specific `seite_geladen` loop.

```python
browser.wait_page_loaded("//div[@id='dashboard']")
```

## Actions

### `wait_and_click(locator: str, by: str = By.XPATH, timeout: float | None = None) -> None`

Waits for the element to be clickable, then clicks it.

```python
browser.wait_and_click("//button[@id='submit']")
```

### `double_click(locator: str, by: str = By.XPATH, pause: float = 0) -> None`

Moves to the element and double-clicks it; optionally sleeps `pause` seconds
afterwards.

```python
browser.double_click("//span[@class='edit']", pause=0.5)
```

### `hover(locator: str, by: str = By.XPATH) -> None`

Moves the mouse to the element.

```python
browser.hover("//div[@id='menu']")
```

### `hover_with_offset(locator: str, x_offset: int, y_offset: int, by: str = By.XPATH) -> None`

Moves to the element, then by an additional `(x_offset, y_offset)`.

```python
browser.hover_with_offset("//div[@id='menu']", 10, 20)
```

### `move_to(locator: str, by: str = By.XPATH) -> None`

Moves to the element and sleeps `poll_pause` seconds.

```python
browser.move_to("//div[@id='tooltip-trigger']")
```

### `wait_move_click(locator: str, by: str = By.XPATH, timeout: float | None = None) -> None`

Waits for clickability, moves to the element, sleeps `poll_pause` seconds, then
clicks it.

```python
browser.wait_move_click("//button[@id='confirm']")
```

### `type_text(locator: str, text: str, by: str = By.XPATH) -> None`

Sends keystrokes to the element.

```python
browser.type_text("//input[@name='email']", "user@example.com")
```

### `upload_file(css_selector: str, path: str) -> None`

Sends a file path to a `<input type="file">` element, located by CSS selector.

```python
browser.upload_file("input[type=file]", "/tmp/photo.png")
```

### `click_in_new_tab(locator: str, check_path: str, by: str = By.XPATH, check_by: str = By.XPATH) -> None`

Ctrl-clicks a link to open it in a new tab, waits for `check_path` to appear in
that tab, closes it, and switches back to the original tab.

```python
browser.click_in_new_tab("//a[@id='external']", "//h1[@id='landed']")
```

## Assertions

### `assert_checkbox_checked(locator: str, by: str = By.XPATH, timeout: float | None = None) -> None`

Raises `AssertionError` if the checkbox is not checked.

```python
browser.assert_checkbox_checked("//input[@id='terms']")
```

### `assert_checkbox_unchecked(locator: str, by: str = By.XPATH, timeout: float | None = None) -> None`

Raises `AssertionError` if the checkbox is checked.

```python
browser.assert_checkbox_unchecked("//input[@id='newsletter']")
```

### `assert_selected_option(locator: str, expected_text: str, by: str = By.XPATH) -> None`

Raises `AssertionError` if the `<select>`'s selected option text does not match
`expected_text`.

```python
browser.assert_selected_option("//select[@id='country']", "Germany")
```

### `assert_present(locator: str, by: str = By.XPATH) -> None`

Raises `AssertionError` if the element is not present.

```python
browser.assert_present("//div[@class='success']")
```

## Frames

### `fill_in_frame(frame_path: str, inner_path: str, text: str, by: str = By.XPATH, submit: bool = True) -> None`

Switches into the frame at `frame_path`, types `text` into `inner_path` inside
it, optionally submits with <kbd>Return</kbd>, then switches back to the
default content. Generic replacement for the app-specific
`switch_and_fill_frame` (which hardcoded a TinyMCE-specific inner path).

```python
browser.fill_in_frame("//iframe[@id='editor']", "//*[@id='tinymce']/p", "Hello world")
```
