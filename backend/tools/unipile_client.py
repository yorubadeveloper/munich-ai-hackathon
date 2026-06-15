"""
Unipile API client.
Handles LinkedIn DM sending and reply checking.
7-day free trial: https://www.unipile.com

Email delivery goes through Resend (https://resend.com) over its HTTP API,
using the shared safe HTTP helper so no extra SDK/SMTP handling is needed.
"""

import logging
from urllib.parse import urlsplit

from config import settings
from tools.safe_http import UnsafeOutboundRequestError, safe_async_client, validate_https_url

log = logging.getLogger(__name__)


# Unipile assigns each account a region-specific DSN (host:port), e.g.
# "api49.unipile.com:17948". Set UNIPILE_DSN in .env to match your dashboard.
def _normalize_unipile_dsn(raw_dsn: str) -> tuple[str, str]:
    dsn = raw_dsn.strip().rstrip("/")
    if not dsn:
        raise UnsafeOutboundRequestError("UNIPILE_DSN is required")

    candidate = dsn if "://" in dsn else f"https://{dsn}"
    parsed = urlsplit(candidate)
    if parsed.scheme != "https":
        raise UnsafeOutboundRequestError("UNIPILE_DSN must use https")
    if parsed.username or parsed.password:
        raise UnsafeOutboundRequestError("UNIPILE_DSN must not include credentials")
    if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise UnsafeOutboundRequestError("UNIPILE_DSN must be a host[:port] value")

    host = (parsed.hostname or "").rstrip(".").lower()
    if host != "unipile.com" and not host.endswith(".unipile.com"):
        raise UnsafeOutboundRequestError("UNIPILE_DSN must point to a unipile.com host")

    try:
        port = parsed.port
    except ValueError as exc:
        raise UnsafeOutboundRequestError("UNIPILE_DSN has an invalid port") from exc

    netloc = host if port is None else f"{host}:{port}"
    return netloc, host


RESEND_ENDPOINT = validate_https_url("https://api.resend.com/emails", {"api.resend.com"})


def _unipile_config() -> tuple[str, str] | None:
    if not settings.unipile_dsn or not settings.unipile_api_key:
        log.warning("Unipile credentials not set - skipping Unipile request.")
        return None
    netloc, host = _normalize_unipile_dsn(settings.unipile_dsn)
    return f"https://{netloc}/api/v1", host


async def send_linkedin_dm(recipient_linkedin_url: str, message: str) -> dict:
    config = _unipile_config()
    if config is None or not settings.unipile_account_id:
        log.warning("Unipile account id not set - skipping LinkedIn DM.")
        return {}
    unipile_base, unipile_host = config
    try:
        async with safe_async_client(allowed_hosts={unipile_host}) as client:
            response = await client.post(
                f"{unipile_base}/messages",
                headers={
                    "X-API-KEY": settings.unipile_api_key,
                    "accept": "application/json",
                    "content-type": "application/json",
                },
                json={
                    "account_id": settings.unipile_account_id,
                    "attendees_ids": [recipient_linkedin_url],
                    "text": message,
                },
                timeout=30,
            )
            return response.json()
    except Exception as e:
        log.warning(f"Unipile LinkedIn DM failed: {e}")
        return {}


async def search_linkedin_people(
    keywords: str,
    company_keyword: str | None = None,
    limit: int = 5,
) -> list[dict]:
    """
    Search LinkedIn people on behalf of the connected account (classic search).
    Used to find a decision-maker (CTO / VP Eng / founder) at a target company.

    Returns a normalized list of:
        {name, headline, role, profile_url, provider_id, location}
    `provider_id` is Unipile's internal person id (the "ACoAA..." value) which is
    what /messages needs as an attendee to actually send a DM.
    """
    config = _unipile_config()
    if config is None or not settings.unipile_account_id:
        return []
    unipile_base, unipile_host = config

    # Combine role keywords with the company so results are scoped to that company.
    kw = keywords
    if company_keyword:
        kw = f"{keywords} {company_keyword}".strip()

    payload = {
        "api": "classic",
        "category": "people",
        "keywords": kw,
    }
    try:
        async with safe_async_client(allowed_hosts={unipile_host}) as client:
            response = await client.post(
                f"{unipile_base}/linkedin/search",
                params={"account_id": settings.unipile_account_id, "limit": limit},
                headers={
                    "X-API-KEY": settings.unipile_api_key,
                    "accept": "application/json",
                    "content-type": "application/json",
                },
                json=payload,
                timeout=40,
            )
            if response.status_code >= 400:
                log.warning(f"Unipile people search failed ({response.status_code}): {response.text[:300]}")
                return []
            items = response.json().get("items", [])
    except Exception as e:
        log.warning(f"Unipile people search error: {e}")
        return []

    people = []
    for it in items:
        if it.get("type") != "PEOPLE":
            continue
        positions = it.get("current_positions") or []
        role = positions[0].get("role") if positions else None
        company_name = positions[0].get("company") if positions else None
        people.append(
            {
                "name": it.get("name"),
                "headline": it.get("headline"),
                "role": role or it.get("headline"),
                "company": company_name,
                "profile_url": it.get("public_profile_url") or it.get("profile_url"),
                "provider_id": it.get("id"),
                "location": it.get("location"),
            }
        )
    return people


async def check_linkedin_replies(conversation_id: str) -> list[dict]:
    config = _unipile_config()
    if config is None:
        return []
    unipile_base, unipile_host = config
    try:
        async with safe_async_client(allowed_hosts={unipile_host}) as client:
            response = await client.get(
                f"{unipile_base}/chats/{conversation_id}/messages",
                headers={"X-API-KEY": settings.unipile_api_key},
                timeout=30,
            )
            messages = response.json().get("items", [])
            return [m for m in messages if not m.get("is_sender")]
    except Exception as e:
        log.warning(f"Unipile reply check failed: {e}")
        return []


async def send_email(to: str, subject: str, body: str) -> dict:
    """Send a plain-text email via Resend's HTTP API."""
    if not settings.resend_api_key or not settings.resend_from_email:
        log.warning("Resend credentials not set - skipping email send.")
        return {}
    try:
        async with safe_async_client(allowed_hosts={"api.resend.com"}) as client:
            response = await client.post(
                RESEND_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {settings.resend_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": settings.resend_from_email,
                    "to": [to],
                    "subject": subject,
                    "text": body,
                },
                timeout=30,
            )
            if response.status_code >= 400:
                log.warning(f"Resend email to {to} failed ({response.status_code}): {response.text[:300]}")
                response.raise_for_status()
            return response.json()
    except Exception as e:
        log.warning(f"Email send to {to} failed: {e}")
        raise
