# tests/test_axe.py
import pytest

pytest.importorskip("axe_selenium_python")

from jc_selenium_helper.axe import assert_no_violations, run_axe  # noqa: E402


def test_run_axe_returns_results(driver, fixture_url):
    driver.get(fixture_url("basic.html"))
    results = run_axe(driver)
    assert "violations" in results


def test_assert_no_violations_raises_on_violation(driver, fixture_url):
    # a11y_bad.html has an <img> with no alt attribute -> at least one violation expected
    driver.get(fixture_url("a11y_bad.html"))
    with pytest.raises(AssertionError):
        assert_no_violations(driver)
