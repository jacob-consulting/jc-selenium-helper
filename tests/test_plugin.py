pytest_plugins = ["pytester"]


def test_jc_chrome_options_fixture_available(pytester):
    pytester.makepyfile(
        """
        def test_options(jc_chrome_options):
            args = jc_chrome_options.arguments
            assert "--headless=new" in args
        """
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
