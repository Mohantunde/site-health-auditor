from site_health_auditor.models import SiteResult


def test_healthy_result() -> None:
    result = SiteResult(
        name="Example",
        url="https://example.com",
        status_code=200,
    )

    assert result.healthy is True


def test_error_result_is_not_healthy() -> None:
    result = SiteResult(
        name="Example",
        url="https://example.com",
        status_code=200,
        error="Parsing error",
    )

    assert result.healthy is False
