# tests/test_browser_actions.py
from pathlib import Path

from selenium.webdriver.common.by import By

FIXTURES = Path(__file__).parent / "fixtures"


def test_type_text(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.type_text("//input[@id='text-input']", "hello")
    assert browser.find("//input[@id='text-input']").get_attribute("value") == "hello"


def test_wait_and_click(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.wait_and_click("//button[@id='clickable']")
    assert browser.find("//button[@id='clickable']").text == "clicked"


def test_double_click(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.double_click("//button[@id='dbl']")
    assert browser.find("//button[@id='dbl']").text == "double"


def test_hover_triggers_mouseover(browser, fixture_url):
    browser.open(fixture_url("dynamic.html"))
    browser.hover("//div[@id='hover-target']")
    assert browser.find("//div[@id='hover-result']").text == "hovered"


def test_move_to_triggers_mouseover(browser, fixture_url):
    browser.open(fixture_url("dynamic.html"))
    browser.move_to("//div[@id='hover-target']")
    assert browser.find("//div[@id='hover-result']").text == "hovered"


def test_click_in_new_tab_returns_to_main(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.click_in_new_tab("//a[@id='newtab']", "//p[@id='target']")
    assert len(browser.driver.window_handles) == 1
    assert browser.find("//h1[@id='title']").text == "Hello"


def test_wait_move_click(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.wait_move_click("//button[@id='clickable']")
    assert browser.find("//button[@id='clickable']").text == "clicked"


def test_upload_file_sets_input_value(browser, fixture_url):
    browser.open(fixture_url("dynamic.html"))
    upload_path = str(FIXTURES / "basic.html")
    browser.upload_file("#upload", upload_path)
    value = browser.find("#upload", by=By.CSS_SELECTOR).get_attribute("value")
    assert value.endswith("basic.html")
