"""Color conversion helpers (replaces the colormap/easydev dependency)."""

from __future__ import annotations


def rgb_to_hex(rgb_string: str) -> str:
    """Convert a CSS ``rgb(...)`` or ``rgba(...)`` string to ``#rrggbb``.

    The alpha channel of ``rgba`` is ignored. Raises ``ValueError`` with a
    descriptive message if the string is not a valid ``rgb()``/``rgba()`` form.
    """
    if "(" not in rgb_string or ")" not in rgb_string:
        raise ValueError(f"Not an rgb()/rgba() string: {rgb_string!r}")
    inner = rgb_string[rgb_string.index("(") + 1 : rgb_string.index(")")]
    components = inner.split(",")
    if len(components) < 3:
        raise ValueError(f"rgb() needs at least 3 components, got {len(components)}: {rgb_string!r}")
    try:
        r, g, b = (int(float(component.strip())) for component in components[:3])
    except ValueError:
        raise ValueError(f"Non-numeric rgb component in {rgb_string!r}") from None
    return f"#{r:02x}{g:02x}{b:02x}"
