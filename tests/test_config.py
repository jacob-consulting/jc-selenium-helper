import pytest

pytest.importorskip("dynaconf")

from jc_selenium_helper.config import get_settings  # noqa: E402


def test_get_settings_reads_relative_file(tmp_path):
    (tmp_path / "settings.yaml").write_text("default:\n  greeting: hi\n")
    anchor = tmp_path / "conftest.py"  # any file whose parent holds the settings
    anchor.write_text("")
    settings = get_settings(anchor, "settings.yaml")
    assert settings.greeting == "hi"


def test_get_settings_missing_file_raises(tmp_path):
    anchor = tmp_path / "conftest.py"
    anchor.write_text("")
    with pytest.raises(AssertionError):
        get_settings(anchor, "nope.yaml")
