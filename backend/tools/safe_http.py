"""Safe outbound HTTP helpers.

The backend only needs to call known SaaS APIs. Keep outbound request targets
allow-listed to prevent SSRF if user-controlled data reaches request inputs.
"""
import re
import socket
from collections.abc import AsyncIterator, Iterable
from contextlib import asynccontextmanager
from ipaddress import ip_address
from urllib.parse import urlsplit, urlunsplit

import httpx


class UnsafeOutboundRequestError(ValueError):
    """Raised when an outbound HTTP request targets an unapproved destination."""


_DOMAIN_LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
_RESERVED_DOMAIN_SUFFIXES = (
    ".localhost",
    ".local",
    ".localdomain",
    ".internal",
    ".test",
    ".example",
    ".invalid",
)


def _normalize_host(host: str | None) -> str:
    if not host:
        raise UnsafeOutboundRequestError("Outbound request host is missing")
    normalized = host.rstrip(".").lower()
    try:
        return normalized.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise UnsafeOutboundRequestError("Outbound request host is invalid") from exc


def _normalize_allowed_hosts(allowed_hosts: Iterable[str]) -> frozenset[str]:
    normalized = frozenset(_normalize_host(host) for host in allowed_hosts)
    if not normalized:
        raise ValueError("At least one allowed outbound host is required")
    return normalized


def validate_https_url(url: str, allowed_hosts: Iterable[str]) -> str:
    """Validate a URL before it is used as an outbound request target."""
    parsed = urlsplit(url)
    host = _normalize_host(parsed.hostname)
    try:
        port = parsed.port
    except ValueError as exc:
        raise UnsafeOutboundRequestError("Outbound URL port is invalid") from exc
    if parsed.scheme != "https":
        raise UnsafeOutboundRequestError("Outbound requests must use https")
    if host not in _normalize_allowed_hosts(allowed_hosts):
        raise UnsafeOutboundRequestError(f"Outbound host is not allowed: {host}")
    if parsed.username or parsed.password:
        raise UnsafeOutboundRequestError("Outbound URLs must not include credentials")
    netloc = host if port is None else f"{host}:{port}"
    return urlunsplit(("https", netloc, parsed.path, parsed.query, parsed.fragment))


def _validate_public_domain(host: str) -> None:
    try:
        ip_address(host)
    except ValueError:
        pass
    else:
        raise UnsafeOutboundRequestError("Public web URLs must use a domain name")

    if host == "localhost" or host.endswith(_RESERVED_DOMAIN_SUFFIXES):
        raise UnsafeOutboundRequestError("Public web URL host is reserved")

    labels = host.split(".")
    if len(labels) < 2:
        raise UnsafeOutboundRequestError("Public web URL host must be a domain name")
    if len(host) > 253:
        raise UnsafeOutboundRequestError("Public web URL host is too long")
    if not all(_DOMAIN_LABEL_RE.fullmatch(label) for label in labels):
        raise UnsafeOutboundRequestError("Public web URL host is invalid")


def _resolved_addresses(host: str) -> frozenset[str]:
    try:
        records = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise UnsafeOutboundRequestError("Public web URL host could not be resolved") from exc

    addresses = frozenset(record[4][0] for record in records)
    if not addresses:
        raise UnsafeOutboundRequestError("Public web URL host could not be resolved")
    return addresses


def _validate_public_resolution(host: str) -> None:
    for address in _resolved_addresses(host):
        parsed = ip_address(address)
        if (
            not parsed.is_global
            or parsed.is_loopback
            or parsed.is_link_local
            or parsed.is_multicast
            or parsed.is_private
            or parsed.is_reserved
            or parsed.is_unspecified
        ):
            raise UnsafeOutboundRequestError(
                "Public web URL host resolves to a non-public address"
            )


def validate_public_https_url(url: str) -> str:
    """Validate a user-provided public web URL before using it in lookups.

    This is intentionally stricter than the SaaS allow-list helper: arbitrary
    company/job URLs must be HTTPS domain names with the default HTTPS port.
    IP literals, localhost, reserved/internal suffixes, alternate ports, and
    embedded credentials are rejected to keep user input away from SSRF targets.
    """
    parsed = urlsplit(url)
    host = _normalize_host(parsed.hostname)
    try:
        port = parsed.port
    except ValueError as exc:
        raise UnsafeOutboundRequestError("Public web URL port is invalid") from exc

    if parsed.scheme != "https":
        raise UnsafeOutboundRequestError("Public web URLs must use https")
    if parsed.username or parsed.password:
        raise UnsafeOutboundRequestError("Public web URLs must not include credentials")
    if port not in (None, 443):
        raise UnsafeOutboundRequestError("Public web URLs must use the default https port")

    _validate_public_domain(host)
    _validate_public_resolution(host)
    netloc = host if port is None else f"{host}:{port}"
    return urlunsplit(("https", netloc, parsed.path, parsed.query, parsed.fragment))


def normalize_public_https_url(url: str) -> str:
    """Normalize optional user URL input to a validated public HTTPS URL."""
    candidate = (url or "").strip()
    if not candidate:
        return ""
    if "://" not in candidate:
        candidate = f"https://{candidate}"
    return validate_public_https_url(candidate)


def public_https_url_host(url: str) -> str:
    """Return the normalized host from a validated public HTTPS URL."""
    parsed = urlsplit(validate_public_https_url(url))
    return _normalize_host(parsed.hostname)


class SafeAsyncClient:
    """Small wrapper that validates concrete URLs before every HTTP request."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        allowed_hosts: Iterable[str],
    ) -> None:
        self._client = client
        self._allowed_hosts = _normalize_allowed_hosts(allowed_hosts)

    def _safe_url(self, url: str) -> str:
        return validate_https_url(str(url), self._allowed_hosts)

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self._client.get(self._safe_url(url), **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self._client.post(self._safe_url(url), **kwargs)


@asynccontextmanager
async def safe_async_client(
    *,
    allowed_hosts: Iterable[str],
    timeout: float = 30,
) -> AsyncIterator[SafeAsyncClient]:
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
        yield SafeAsyncClient(client, normalized_allowed_hosts)
