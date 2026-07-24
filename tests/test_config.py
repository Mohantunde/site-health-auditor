from pathlib import Path

import pytest

from site_health_auditor.config import ConfigError, load_sites


def test_load_sites_skips_disabled_entries(tmp_path: Path) -> None:
    config = tmp_path / "sites.yml"
    config.write_text(
        '''
sites:
  - name: Enabled
    url: https://example.com
    enabled: true
  - name: Disabled
    url: https://example.org
    enabled: false
''',
        encoding="utf-8",
    )

    sites = load_sites(config)

    assert sites == [{"name": "Enabled", "url": "https://example.com"}]


def test_load_sites_rejects_invalid_url(tmp_path: Path) -> None:
    config = tmp_path / "sites.yml"
    config.write_text(
        '''
sites:
  - name: Broken
    url: example.com
''',
        encoding="utf-8",
    )

    with pytest.raises(ConfigError):
        load_sites(config)
