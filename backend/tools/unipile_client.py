"""
Unipile API client.
Handles LinkedIn DM sending and reply checking.
7-day free trial: https://www.unipile.com

Email delivery goes through Resend (https://resend.com) over its HTTP API,
reusing httpx so no extra SDK/SMTP handling is needed.
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


_unipile_netloc, UNIPILE_HOST = _normalize_unipile_dsn(settings.unipile_dsn)
UNIPILE_BASE = f"https://{_unipile_netloc}/api/v1"
RESEND_ENDPOINT = validate_https_url("https://api.resend.com/emails", {"api.resend.com"})


async def send_linkedin_dm(recipient_linkedin_url: str, message: str) -> dict:
    try:
        async with safe_async_client(allowed_hosts={UNIPILE_HOST}) as client:
            response = await client.post(
                f"{UNIPILE_BASE}/messages",
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


async def check_linkedin_replies(conversation_id: str) -> list[dict]:
    try:
        async with safe_async_client(allowed_hosts={UNIPILE_HOST}) as client:
            response = await client.get(
                f"{UNIPILE_BASE}/chats/{conversation_id}/messages",
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
    if not settings.resend_api_key:
        log.warning("RESEND_API_KEY not set — skipping email send.")
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
                log.warning(
                    f"Resend email to {to} failed "
                    f"({response.status_code}): {response.text[:300]}"
                )
                response.raise_for_status()
            return response.json()
    except Exception as e:
        log.warning(f"Email send to {to} failed: {e}")
        raise
