from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import yaml


class ConfigError(ValueError):
    pass


def load_sites(path: str | Path) -> list[dict[str, str]]:
    config_path = Path(path)

    if not config_path.exists():
        raise ConfigError(f"Configuration file not found: {config_path}")

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML: {exc}") from exc

    entries = raw.get("sites")
    if not isinstance(entries, list):
        raise ConfigError("Configuration must contain a 'sites' list.")

    sites: list[dict[str, str]] = []

    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise ConfigError(f"Site entry #{index} must be a mapping.")

        if entry.get("enabled", True) is False:
            continue

        name = str(entry.get("name", "")).strip()
        url = str(entry.get("url", "")).strip()

        if not name:
            raise ConfigError(f"Site entry #{index} is missing a name.")

        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ConfigError(
                f"Site entry #{index} has an invalid URL: {url!r}. "
                "Use a full URL such as https://example.com"
            )

        sites.append({"name": name, "url": url})

    if not sites:
        raise ConfigError("No enabled sites were found.")

    return sites
