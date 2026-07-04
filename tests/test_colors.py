import pytest

from jc_selenium_helper.colors import rgb_to_hex


@pytest.mark.parametrize(
    "value, expected",
    [
        ("rgb(255, 0, 0)", "#ff0000"),
        ("rgb(0, 128, 0)", "#008000"),
        ("rgba(16, 32, 48, 0.5)", "#102030"),
        ("rgb(0,0,0)", "#000000"),
    ],
)
def test_rgb_to_hex(value, expected):
    assert rgb_to_hex(value) == expected
