"""Optional Dynaconf settings loader (requires the ``config`` extra)."""

from __future__ import annotations

from pathlib import Path

from dynaconf import Dynaconf
from dynaconf.base import Settings


def get_settings(location: str | Path, *files: str) -> Settings:
    """Build a Dynaconf ``Settings`` from files resolved next to ``location``.

    ``location`` is typically ``__file__`` of the caller; each name in ``files``
    is resolved against ``Path(location).parent`` and must exist.
    """
    parent = Path(location).parent
    settings_files = []
    for name in files:
        settings_file = (parent / name).resolve()
        assert settings_file.exists(), f"settings file not found: {settings_file}"
        settings_files.append(settings_file)
    return Dynaconf(
        environments=True,
        envvar_prefix="SELENIUM",
        env_switcher="SELENIUM_ENVIRONMENT",
        settings_files=settings_files,
    )
