"""Safe outbound HTTP helpers.

The backend only needs to call known SaaS APIs. Keep outbound request targets
allow-listed to prevent SSRF if user-controlled data reaches request inputs.
"""
from collections.abc import AsyncIterator, Iterable
from contextlib import asynccontextmanager
from urllib.parse import urlsplit

import httpx


class UnsafeOutboundRequestError(ValueError):
    """Raised when an outbound HTTP request targets an unapproved destination."""


def _normalize_host(host: str | None) -> str:
    if not host:
        raise UnsafeOutboundRequestError("Outbound request host is missing")
    return host.rstrip(".").lower()


def _normalize_allowed_hosts(allowed_hosts: Iterable[str]) -> frozenset[str]:
    normalized = frozenset(_normalize_host(host) for host in allowed_hosts)
    if not normalized:
        raise ValueError("At least one allowed outbound host is required")
    return normalized


def validate_https_url(url: str, allowed_hosts: Iterable[str]) -> str:
    """Validate a URL before it is used as an outbound request target."""
    parsed = urlsplit(url)
    host = _normalize_host(parsed.hostname)
    if parsed.scheme != "https":
        raise UnsafeOutboundRequestError("Outbound requests must use https")
    if host not in _normalize_allowed_hosts(allowed_hosts):
        raise UnsafeOutboundRequestError(f"Outbound host is not allowed: {host}")
    if parsed.username or parsed.password:
        raise UnsafeOutboundRequestError("Outbound URLs must not include credentials")
    return url


@asynccontextmanager
async def safe_async_client(
    *,
    allowed_hosts: Iterable[str],
    timeout: float = 30,
) -> AsyncIterator[httpx.AsyncClient]:
    """Create an AsyncClient that rejects requests outside allowed HTTPS hosts.

    Redirect following is disabled so a trusted endpoint cannot bounce the server
    to metadata services, loopback, or internal network destinations.
    """
    normalized_allowed_hosts = _normalize_allowed_hosts(allowed_hosts)

    async def validate_request(request: httpx.Request) -> None:
        host = _normalize_host(request.url.host)
        if request.url.scheme != "https":
            raise UnsafeOutboundRequestError("Outbound requests must use https")
        if host not in normalized_allowed_hosts:
            raise UnsafeOutboundRequestError(f"Outbound host is not allowed: {host}")
        if request.url.username or request.url.password:
            raise UnsafeOutboundRequestError("Outbound URLs must not include credentials")

    async with httpx.AsyncClient(
        event_hooks={"request": [validate_request]},
        follow_redirects=False,
        timeout=timeout,
        trust_env=False,
    ) as client:
        yield client
