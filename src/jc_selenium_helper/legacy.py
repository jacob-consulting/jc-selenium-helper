# src/jc_selenium_helper/legacy.py
"""Backwards-compatible adapter exposing the original German/ad-hoc API.

Existing suites can migrate by replacing::

    from libs.browser import Browser

with::

    from jc_selenium_helper.legacy import Browser

Every legacy method emits a ``DeprecationWarning`` and delegates to the clean
:class:`jc_selenium_helper.browser.Browser` API. One method (``seite_geladen``)
keeps its original app-specific behavior verbatim so existing tests are
unaffected.
"""

from __future__ import annotations

import time
import warnings

from selenium.webdriver.common.by import By

from jc_selenium_helper.browser import Browser as _Browser
from jc_selenium_helper.colors import rgb_to_hex


def _deprecated(old: str, new: str) -> None:
    warnings.warn(
        f"{old}() is deprecated; use {new}() instead.",
        DeprecationWarning,
        stacklevel=3,
    )


class LegacyBrowser(_Browser):
    """Deprecated German-named API preserved for existing test suites."""

    def xpath(self, xpath):
        _deprecated("xpath", "find")
        return self.find(xpath)

    def xpaths(self, xpath):
        _deprecated("xpaths", "find_all")
        return self.find_all(xpath)

    def css(self, selector):
        _deprecated("css", "find")
        return self.find(selector, by=By.CSS_SELECTOR)

    def get_elements(self, path):
        _deprecated("get_elements", "find_all")
        return self.find_all(path)

    def check_exists_by_xpath(self, path):
        _deprecated("check_exists_by_xpath", "exists")
        return self.exists(path)

    def wait_element_present(self, path, time_to_wait=None):
        _deprecated("wait_element_present", "wait_present")
        return self.wait_present(path, timeout=time_to_wait)

    def wait_element_not_present(self, path, time_to_wait=None):
        _deprecated("wait_element_not_present", "wait_not_present")
        return self.wait_not_present(path, timeout=time_to_wait)

    def wait_element_clickable(self, path, time_to_wait=None):
        _deprecated("wait_element_clickable", "wait_clickable")
        return self.wait_clickable(path, timeout=time_to_wait)

    def inhalt_geladen(self):
        _deprecated("inhalt_geladen", "wait_document_ready")
        return self.wait_document_ready()

    def doppelclick_element(self, pause, hover):
        _deprecated("doppelclick_element", "double_click")
        return self.double_click(hover, pause=pause)

    def hover_element(self, hover):
        _deprecated("hover_element", "hover")
        return self.hover(hover)

    def hover_element_with_offset(self, hover, x_offset, y_offset):
        _deprecated("hover_element_with_offset", "hover_with_offset")
        return self.hover_with_offset(hover, x_offset, y_offset)

    def move_to_element(self, path):
        _deprecated("move_to_element", "move_to")
        return self.move_to(path)

    def wait_move_click_element(self, path, time_to_wait=None):
        _deprecated("wait_move_click_element", "wait_move_click")
        return self.wait_move_click(path, timeout=time_to_wait)

    def click_new_tab(self, path, check_path):
        _deprecated("click_new_tab", "click_in_new_tab")
        return self.click_in_new_tab(path, check_path)

    def eingabe(self, path, text):
        _deprecated("eingabe", "type_text")
        return self.type_text(path, text)

    def eingabe_upload_css(self, path, text):
        _deprecated("eingabe_upload_css", "upload_file")
        return self.upload_file(path, text)

    def assert_checkbox_is_checked(self, path, time_to_wait=None):
        _deprecated("assert_checkbox_is_checked", "assert_checkbox_checked")
        return self.assert_checkbox_checked(path, timeout=time_to_wait)

    def assert_checkbox_is_not_checked(self, path, time_to_wait=None):
        _deprecated("assert_checkbox_is_not_checked", "assert_checkbox_unchecked")
        return self.assert_checkbox_unchecked(path, timeout=time_to_wait)

    def check_select(self, path, exp_text):
        _deprecated("check_select", "assert_selected_option")
        return self.assert_selected_option(path, exp_text)

    def ele_test(self, path):
        _deprecated("ele_test", "assert_present")
        return self.assert_present(path)

    @staticmethod
    def switch_rgb(color_rgb):
        _deprecated("switch_rgb", "colors.rgb_to_hex")
        return rgb_to_hex(color_rgb)

    # -- verbatim app-specific behavior (unchanged for compatibility) --
    def seite_geladen(self, check_path):
        _deprecated("seite_geladen", "wait_page_loaded")
        time_counter = 0
        time.sleep(1)
        while True:
            element = self.driver.find_elements(By.XPATH, check_path)
            if element:
                break
            self.driver.refresh()
            time.sleep(10)
            time_counter += 1
            if time_counter > 5:
                raise ValueError("Seite nicht geladen")
        self.inhalt_geladen()


# Drop-in module-level alias: ``from jc_selenium_helper.legacy import Browser``
Browser = LegacyBrowser
