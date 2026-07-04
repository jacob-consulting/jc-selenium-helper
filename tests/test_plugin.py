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


def test_conftest_override_feeds_jc_options_into_chrome_options(pytester):
    # The documented wiring: a one-line chrome_options override in the project
    # conftest deterministically takes precedence over pytest-selenium's own
    # chrome_options, so jc defaults flow into the driver.
    pytester.makeconftest(
        """
        import pytest


        @pytest.fixture
        def chrome_options(jc_chrome_options):
            return jc_chrome_options
        """
    )
    pytester.makepyfile(
        """
        def test_jc_defaults_present(chrome_options, jc_chrome_options):
            assert chrome_options is jc_chrome_options
            assert "--headless=new" in chrome_options.arguments
        """
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_conftest_override_can_customize_jc_options(pytester):
    pytester.makeconftest(
        """
        import pytest


        @pytest.fixture
        def chrome_options(jc_chrome_options):
            jc_chrome_options.add_argument("--window-size=1920,1080")
            return jc_chrome_options
        """
    )
    pytester.makepyfile(
        """
        def test_customization_flows_through(chrome_options):
            assert "--window-size=1920,1080" in chrome_options.arguments
            assert "--headless=new" in chrome_options.arguments
        """
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
