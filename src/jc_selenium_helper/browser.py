# src/jc_selenium_helper/browser.py
"""A thin, ergonomic wrapper around a Selenium WebDriver."""

from __future__ import annotations

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


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
