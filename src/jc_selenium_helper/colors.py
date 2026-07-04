"""Color conversion helpers (replaces the colormap/easydev dependency)."""

from __future__ import annotations


def rgb_to_hex(rgb_string: str) -> str:
    """Convert a CSS ``rgb(...)`` or ``rgba(...)`` string to ``#rrggbb``.

    The alpha channel of ``rgba`` is ignored.
    """
    inner = rgb_string[rgb_string.index("(") + 1 : rgb_string.index(")")]
    parts = [int(float(component.strip())) for component in inner.split(",")[:3]]
    r, g, b = parts
    return f"#{r:02x}{g:02x}{b:02x}"
