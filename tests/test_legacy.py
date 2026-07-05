# tests/test_legacy.py
import pytest

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
