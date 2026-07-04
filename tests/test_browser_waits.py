# tests/test_browser_waits.py
import pytest
from selenium.common.exceptions import TimeoutException


def test_wait_present_returns_element(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    assert browser.wait_present("//span[@id='late']").text == "here"


def test_wait_present_times_out(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    with pytest.raises(TimeoutException):
        browser.wait_present("//span[@id='never']", timeout=1)


def test_wait_clickable_returns_element(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    assert browser.wait_clickable("//button[@id='btn']").tag_name == "button"


def test_wait_document_ready(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.wait_document_ready()  # should not raise


def test_wait_page_loaded_on_present_element(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.wait_page_loaded("//h1[@id='title']", retries=1, interval=1)


def test_wait_not_present_returns_true_when_element_disappears(browser, fixture_url):
    browser.open(fixture_url("dynamic.html"))
    assert browser.wait_not_present("//div[@id='vanishing']") is True


def test_wait_not_present_times_out_when_element_stays(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    with pytest.raises(TimeoutException, match="still present"):
        browser.wait_not_present("//h1[@id='title']", timeout=1)
