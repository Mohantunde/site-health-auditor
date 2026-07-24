from __future__ import annotations

import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .models import SiteResult

USER_AGENT = (
    "SiteHealthAuditor/0.1 "
    "(https://github.com/Mohantunde/site-health-auditor)"
)


def _safe_text(value: str | None) -> str:
    return " ".join((value or "").split())


def _head_or_get(session: requests.Session, url: str, timeout: float) -> bool:
    try:
        response = session.head(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )
        if response.status_code in {403, 405}:
            response = session.get(
                url,
                timeout=timeout,
                allow_redirects=True,
                headers={"User-Agent": USER_AGENT},
                stream=True,
            )
        return 200 <= response.status_code < 400
    except requests.RequestException:
        return False


def audit_site(name: str, url: str, timeout: float = 15.0) -> SiteResult:
    result = SiteResult(name=name, url=url)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    try:
        started = time.perf_counter()
        response = session.get(url, timeout=timeout, allow_redirects=True)
        result.response_time_seconds = round(time.perf_counter() - started, 3)
        result.status_code = response.status_code
        result.final_url = response.url
        result.uses_https = urlparse(response.url).scheme.lower() == "https"

        content_type = response.headers.get("content-type", "").lower()
        if "html" not in content_type:
            result.error = f"Expected HTML but received: {content_type or 'unknown'}"
            return result

        soup = BeautifulSoup(response.text, "html.parser")

        if soup.title:
            result.title = _safe_text(soup.title.get_text())
            result.title_length = len(result.title)

        description = soup.find(
            "meta",
            attrs={"name": lambda x: x and x.lower() == "description"},
        )
        if description:
            result.meta_description = _safe_text(description.get("content"))
            result.meta_description_length = len(result.meta_description)

        result.h1_count = len(soup.find_all("h1"))

        canonical = soup.find(
            "link",
            attrs={
                "rel": lambda x: x
                and "canonical" in [str(item).lower() for item in x]
            },
        )
        if canonical:
            result.canonical_url = _safe_text(canonical.get("href"))

        robots = soup.find(
            "meta",
            attrs={"name": lambda x: x and x.lower() == "robots"},
        )
        if robots:
            result.robots_meta = _safe_text(robots.get("content"))

        parsed = urlparse(response.url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        result.robots_txt_found = _head_or_get(
            session,
            urljoin(base_url, "/robots.txt"),
            timeout,
        )

        for candidate in (
            "/sitemap.xml",
            "/sitemap_index.xml",
            "/wp-sitemap.xml",
        ):
            sitemap_url = urljoin(base_url, candidate)
            if _head_or_get(session, sitemap_url, timeout):
                result.sitemap_found = True
                result.sitemap_url = sitemap_url
                break

    except requests.Timeout:
        result.error = f"Request timed out after {timeout:g} seconds"
    except requests.RequestException as exc:
        result.error = str(exc)
    except Exception as exc:
        result.error = f"Unexpected error: {exc}"
    finally:
        session.close()

    return result
