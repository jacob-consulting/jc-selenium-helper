# Config

Optional [Dynaconf](https://www.dynaconf.com/) settings loader (requires the
`config` extra: `pip install "jc-selenium-helper[config]"`).

### `get_settings(location: str | Path, *files: str) -> Settings`

Builds a Dynaconf `Settings` object from settings files resolved next to
`location` (typically `__file__` of the caller). Each name in `files` is
resolved against `Path(location).parent`; an `AssertionError` is raised if any
named file does not exist.

The resulting `Settings` has:

- `environments=True` — supports `[default]`/environment sections.
- `envvar_prefix="SELENIUM"` — environment variable overrides use the
  `SELENIUM_` prefix.
- `env_switcher="SELENIUM_ENVIRONMENT"` — set this environment variable to
  switch which environment section is active.

```python
from jc_selenium_helper.config import get_settings

settings = get_settings(__file__, "settings.yaml", "settings.local.yaml")
settings.BASE_URL
```
