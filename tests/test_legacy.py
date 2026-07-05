# tests/test_legacy.py
from pathlib import Path

import pytest
from selenium.webdriver.common.by import By

from jc_selenium_helper.legacy import Browser as LegacyBrowser


def test_legacy_eingabe_delegates_and_warns(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("basic.html"))
    with pytest.warns(DeprecationWarning):
        legacy.eingabe("//input[@id='text-input']", "legacy")
    assert legacy.find("//input[@id='text-input']").get_attribute("value") == "legacy"


def test_legacy_check_exists_by_xpath(driver, fixture_url):
    legacy = LegacyBrowser(driver, default_timeout=10, poll_pause=0.2)
    legacy.open(fixture_url("basic.html"))
    with pytest.warns(DeprecationWarning):
        assert legacy.check_exists_by_xpath("//h1[@id='title']") is True


def test_legacy_switch_rgb_static():
    with pytest.warns(DeprecationWarning):
        assert LegacyBrowser.switch_rgb("rgb(255, 0, 0)") == "#ff0000"


def test_switch_and_fill_frame_removed():
    # M1.1: the unrunnable legacy method was deleted; callers use fill_in_frame.
    assert not hasattr(LegacyBrowser, "switch_and_fill_frame")


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
