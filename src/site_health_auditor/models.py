from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class SiteResult:
    name: str
    url: str
    final_url: str = ""
    status_code: int | None = None
    response_time_seconds: float | None = None
    uses_https: bool = False
    title: str = ""
    title_length: int = 0
    meta_description: str = ""
    meta_description_length: int = 0
    h1_count: int = 0
    canonical_url: str = ""
    robots_meta: str = ""
    robots_txt_found: bool = False
    sitemap_found: bool = False
    sitemap_url: str = ""
    error: str = ""

    @property
    def healthy(self) -> bool:
        return (
            not self.error
            and self.status_code is not None
            and 200 <= self.status_code < 400
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["healthy"] = self.healthy
        return data
