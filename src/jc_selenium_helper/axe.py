"""Optional accessibility checks via axe-core (requires the ``axe`` extra)."""

from __future__ import annotations

from axe_selenium_python import Axe


def run_axe(driver) -> dict:
    """Inject axe-core into the current page and return the raw results dict."""
    axe = Axe(driver)
    axe.inject()
    return axe.run()


def assert_no_violations(driver) -> None:
    """Run axe-core and raise ``AssertionError`` if any violations are found."""
    results = run_axe(driver)
    violations = results.get("violations", [])
    if violations:
        ids = ", ".join(v["id"] for v in violations)
        raise AssertionError(f"{len(violations)} accessibility violation(s): {ids}")
