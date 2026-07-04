# tests/test_browser_finders.py
from selenium.webdriver.common.by import By


def test_find_returns_element(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    assert browser.find("//h1[@id='title']").text == "Hello"


def test_find_with_css(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    assert browser.find("#title", by=By.CSS_SELECTOR).text == "Hello"


def test_find_all_returns_list(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    items = browser.find_all("//li[@class='item']")
    assert [e.text for e in items] == ["a", "b", "c"]


def test_exists_true_and_false(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    assert browser.exists("//h1[@id='title']") is True
    assert browser.exists("//h1[@id='missing']") is False
