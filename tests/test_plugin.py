pytest_plugins = ["pytester"]


def test_jc_chrome_options_safe_by_default(pytester):
    pytester.makepyfile(
        """
        def test_options(jc_chrome_options):
            args = jc_chrome_options.arguments
            assert "--headless=new" in args
            assert "--no-sandbox" not in args
            assert "--ignore-certificate-errors" not in args
        """
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1, warnings=0)


def test_jc_insecure_chrome_fixture_opts_in_and_warns(pytester):
    pytester.makeconftest(
        """
        import pytest


        @pytest.fixture
        def jc_insecure_chrome():
            return True
        """
    )
    pytester.makepyfile(
        """
        def test_insecure_flags_present(jc_chrome_options):
            args = jc_chrome_options.arguments
            assert "--no-sandbox" in args
            assert "--ignore-certificate-errors" in args
        """
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1, warnings=1)


def test_env_var_opts_in_and_warns(pytester, monkeypatch):
    monkeypatch.setenv("JC_SELENIUM_INSECURE", "1")
    pytester.makepyfile(
        """
        def test_insecure_flags_present(jc_chrome_options):
            args = jc_chrome_options.arguments
            assert "--no-sandbox" in args
            assert "--ignore-certificate-errors" in args
        """
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1, warnings=1)


def test_env_var_falsey_stays_safe(pytester, monkeypatch):
    monkeypatch.setenv("JC_SELENIUM_INSECURE", "0")
    pytester.makepyfile(
        """
        def test_no_insecure_flags(jc_chrome_options):
            args = jc_chrome_options.arguments
            assert "--no-sandbox" not in args
            assert "--ignore-certificate-errors" not in args
        """
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1, warnings=0)


def test_chrome_options_feeds_pytest_selenium(pytester):
    pytester.makepyfile(
        """
        def test_same_object(chrome_options, jc_chrome_options):
            assert chrome_options is jc_chrome_options
        """
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_chrome_options_reflects_jc_chrome_options_override(pytester):
    pytester.makeconftest(
        """
        import pytest
        from selenium.webdriver.chrome.options import Options


        @pytest.fixture
        def jc_chrome_options():
            options = Options()
            options.add_argument("--window-size=1920,1080")
            return options
        """
    )
    pytester.makepyfile(
        """
        def test_override_flows_through(chrome_options):
            assert "--window-size=1920,1080" in chrome_options.arguments
        """
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
