# tests/test_browser_assertions.py
import pytest


def test_assert_checkbox_checked_passes(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.assert_checkbox_checked("//input[@id='checked-box']")


def test_assert_checkbox_checked_fails(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    with pytest.raises(AssertionError):
        browser.assert_checkbox_checked("//input[@id='unchecked-box']")


def test_assert_checkbox_unchecked_passes(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.assert_checkbox_unchecked("//input[@id='unchecked-box']")


def test_assert_checkbox_unchecked_fails(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    with pytest.raises(AssertionError):
        browser.assert_checkbox_unchecked("//input[@id='checked-box']")


def test_assert_selected_option_passes(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.assert_selected_option("//select[@id='picker']", "two")


def test_assert_selected_option_fails(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    with pytest.raises(AssertionError):
        browser.assert_selected_option("//select[@id='picker']", "one")


def test_assert_present_fails_when_missing(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    with pytest.raises(AssertionError):
        browser.assert_present("//div[@id='nope']")
