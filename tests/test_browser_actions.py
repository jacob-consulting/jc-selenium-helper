# tests/test_browser_actions.py
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


def test_hover_does_not_raise(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.hover("//button[@id='clickable']")


def test_move_to_does_not_raise(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.move_to("//button[@id='clickable']")


def test_click_in_new_tab_returns_to_main(browser, fixture_url):
    browser.open(fixture_url("basic.html"))
    browser.click_in_new_tab("//a[@id='newtab']", "//p[@id='target']")
    assert len(browser.driver.window_handles) == 1
    assert browser.find("//h1[@id='title']").text == "Hello"
