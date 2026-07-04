# src/jc_selenium_helper/browser.py
"""A thin, ergonomic wrapper around a Selenium WebDriver."""

from __future__ import annotations

import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
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
        WebDriverWait(self.driver, self._timeout(timeout)).until(
            EC.presence_of_element_located((by, locator))
        )
        return self.driver.find_element(by, locator)

    def wait_clickable(self, locator: str, by: str = By.XPATH, timeout: float | None = None) -> WebElement:
        WebDriverWait(self.driver, self._timeout(timeout)).until(
            EC.element_to_be_clickable((by, locator))
        )
        return self.driver.find_element(by, locator)

    def wait_not_present(self, locator: str, by: str = By.XPATH, timeout: float | None = None) -> bool:
        seconds = self._timeout(timeout)
        try:
            WebDriverWait(self.driver, seconds).until(
                EC.invisibility_of_element_located((by, locator))
            )
        except TimeoutException as exc:
            raise TimeoutException(
                f"Element '{locator}' still present after {seconds}s"
            ) from exc
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
