# src/jc_selenium_helper/browser.py
"""A thin, ergonomic wrapper around a Selenium WebDriver."""

from __future__ import annotations

import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait


class Browser:
    """Wraps a Selenium ``WebDriver`` with convenience helpers.

    Locators default to XPath; pass ``by=By.CSS_SELECTOR`` (or any Selenium
    ``By`` value) to use a different strategy.
    """

    def __init__(self, driver, default_timeout: float = 120, poll_pause: float = 1) -> None:
        self.driver = driver
        self.default_timeout = default_timeout
        self.poll_pause = poll_pause

    # -- navigation --
    def open(self, url: str) -> None:
        self.driver.get(url)

    # -- finders --
    def find(self, locator: str, by: str = By.XPATH) -> WebElement:
        return self.driver.find_element(by, locator)

    def find_all(self, locator: str, by: str = By.XPATH) -> list[WebElement]:
        return self.driver.find_elements(by, locator)

    def exists(self, locator: str, by: str = By.XPATH) -> bool:
        try:
            self.driver.find_element(by, locator)
        except NoSuchElementException:
            return False
        return True

    # -- waits --
    def _timeout(self, timeout: float | None) -> float:
        return self.default_timeout if timeout is None else timeout

    def wait_present(self, locator: str, by: str = By.XPATH, timeout: float | None = None) -> WebElement:
        WebDriverWait(self.driver, self._timeout(timeout)).until(EC.presence_of_element_located((by, locator)))
        return self.driver.find_element(by, locator)

    def wait_clickable(self, locator: str, by: str = By.XPATH, timeout: float | None = None) -> WebElement:
        WebDriverWait(self.driver, self._timeout(timeout)).until(EC.element_to_be_clickable((by, locator)))
        return self.driver.find_element(by, locator)

    def wait_not_present(self, locator: str, by: str = By.XPATH, timeout: float | None = None) -> bool:
        seconds = self._timeout(timeout)
        try:
            WebDriverWait(self.driver, seconds).until(EC.invisibility_of_element_located((by, locator)))
        except TimeoutException as exc:
            raise TimeoutException(f"Element '{locator}' still present after {seconds}s") from exc
        return True

    def wait_document_ready(self, timeout: float | None = None) -> None:
        seconds = self._timeout(timeout)
        elapsed = 0.0
        while self.driver.execute_script("return document.readyState") != "complete":
            time.sleep(self.poll_pause)
            elapsed += self.poll_pause
            if elapsed > seconds:
                raise TimeoutError("document.readyState never reached 'complete'")

    def wait_page_loaded(
        self,
        check_path: str,
        by: str = By.XPATH,
        retries: int = 5,
        interval: float = 10,
    ) -> None:
        """Wait for ``check_path`` to appear, refreshing between attempts.

        Generic replacement for the app-specific ``seite_geladen`` loop.
        """
        time.sleep(self.poll_pause)
        attempt = 0
        while not self.driver.find_elements(by, check_path):
            self.driver.refresh()
            time.sleep(interval)
            attempt += 1
            if attempt > retries:
                raise TimeoutError(f"Page not loaded (missing {check_path})")
        self.wait_document_ready()

    # -- actions --
    def wait_and_click(self, locator: str, by: str = By.XPATH, timeout: float | None = None) -> None:
        self.wait_clickable(locator, by, timeout).click()

    def double_click(self, locator: str, by: str = By.XPATH, pause: float = 0) -> None:
        element = self.find(locator, by)
        ActionChains(self.driver).move_to_element(element).double_click().perform()
        if pause:
            time.sleep(pause)

    def hover(self, locator: str, by: str = By.XPATH) -> None:
        element = self.find(locator, by)
        ActionChains(self.driver).move_to_element(element).perform()

    def hover_with_offset(self, locator: str, x_offset: int, y_offset: int, by: str = By.XPATH) -> None:
        element = self.find(locator, by)
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        actions.move_by_offset(x_offset, y_offset).perform()

    def move_to(self, locator: str, by: str = By.XPATH) -> None:
        element = self.find(locator, by)
        ActionChains(self.driver).move_to_element(element).perform()
        time.sleep(self.poll_pause)

    def wait_move_click(self, locator: str, by: str = By.XPATH, timeout: float | None = None) -> None:
        element = self.wait_clickable(locator, by, timeout)
        ActionChains(self.driver).move_to_element(element).perform()
        time.sleep(self.poll_pause)
        element.click()

    def type_text(self, locator: str, text: str, by: str = By.XPATH) -> None:
        self.find(locator, by).send_keys(text)

    def upload_file(self, css_selector: str, path: str) -> None:
        self.driver.find_element(By.CSS_SELECTOR, css_selector).send_keys(path)

    def click_in_new_tab(
        self,
        locator: str,
        check_path: str,
        by: str = By.XPATH,
        check_by: str = By.XPATH,
    ) -> None:
        """Ctrl-click a link, verify the new tab, close it, return to the first tab."""
        element = self.find(locator, by)
        ActionChains(self.driver).key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.wait_present(check_path, check_by)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    # -- assertions --
    def assert_checkbox_checked(self, locator: str, by: str = By.XPATH, timeout: float | None = None) -> None:
        if not self.wait_present(locator, by, timeout).is_selected():
            raise AssertionError(f"Checkbox is not checked: {locator}")

    def assert_checkbox_unchecked(self, locator: str, by: str = By.XPATH, timeout: float | None = None) -> None:
        if self.wait_present(locator, by, timeout).is_selected():
            raise AssertionError(f"Checkbox is checked: {locator}")

    def assert_selected_option(self, locator: str, expected_text: str, by: str = By.XPATH) -> None:
        select = Select(self.find(locator, by))
        actual = select.first_selected_option.text
        if actual != expected_text:
            raise AssertionError(f"Selected option '{actual}' != expected '{expected_text}'")

    def assert_present(self, locator: str, by: str = By.XPATH) -> None:
        if not self.exists(locator, by):
            raise AssertionError(f"Element not present: {locator}")

    # -- frames --
    def fill_in_frame(
        self,
        frame_path: str,
        inner_path: str,
        text: str,
        by: str = By.XPATH,
        submit: bool = True,
    ) -> None:
        """Switch into ``frame_path``, type ``text`` into ``inner_path``, switch back.

        Generic replacement for the app-specific ``switch_and_fill_frame`` (which
        hardcoded the TinyMCE inner path).
        """
        frame = self.find(frame_path, by)
        self.driver.switch_to.frame(frame)
        try:
            self.type_text(inner_path, text)
            if submit:
                self.type_text(inner_path, Keys.RETURN)
        finally:
            self.driver.switch_to.default_content()
