# tests/test_browser_frame.py
def test_fill_in_frame(browser, fixture_url):
    browser.open(fixture_url("frame.html"))
    browser.fill_in_frame(
        "//iframe[@id='editor']",
        "//input[@id='inner-input']",
        "typed",
        submit=False,
    )
    browser.driver.switch_to.frame(browser.find("//iframe[@id='editor']"))
    assert browser.find("//input[@id='inner-input']").get_attribute("value") == "typed"
    browser.driver.switch_to.default_content()
