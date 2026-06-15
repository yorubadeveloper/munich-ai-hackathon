"""
Telegram outbound helpers — approval requests, reply notifications, follow-ups.
These send messages with inline keyboards; the callbacks are handled in tg/bot.py.
"""

import logging

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

from config import settings

log = logging.getLogger(__name__)

bot = Bot(token=settings.telegram_bot_token) if settings.telegram_bot_token else None


async def _send_message(**kwargs):
    if bot is None or not settings.telegram_chat_id:
        log.warning("Telegram credentials not set - skipping outbound message.")
        return
    await bot.send_message(**kwargs)


def _escape_md(text: str) -> str:
    """Escape MarkdownV1 special chars so drafts with _ * etc. don't break."""
    if not text:
        return ""
    for ch in ("_", "*", "`", "["):
        text = text.replace(ch, f"\\{ch}")
    return text


async def send_approval_request(company, draft, research=None):
    score = company.fit_score or 0

    # Company context line.
    summary = ""
    contact_line = ""
    if research is not None:
        if getattr(research, "recent_news", None):
            summary = _escape_md(research.recent_news[:220])
        name = getattr(research, "hiring_manager_name", None)
        role = getattr(research, "hiring_manager_role", None)
        if name:
            contact_line = f"\U0001f464 To: {_escape_md(name)}"
            if role:
                contact_line += f" ({_escape_md(role)})"
            contact_line += "\n"

    channel_label = "LinkedIn DM" if draft.channel == "linkedin" else "Email"
    subject_line = ""
    if draft.channel == "email" and getattr(draft, "subject", ""):
        subject_line = f"*Subject:* {_escape_md(draft.subject)}\n"

    text = (
        f"\U0001f3af *New match ready*\n\n"
        f"*{_escape_md(company.name)}*  ·  {score:.1f}/10  ·  {channel_label}\n"
        f"{contact_line}" + (f"_{summary}_\n" if summary else "") + f"\n{subject_line}"
        f"*Draft:*\n{_escape_md(draft.body[:700])}"
    )
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("\u2705 Send it", callback_data=f"approve:{company.id}"),
                InlineKeyboardButton("\u274c Skip", callback_data=f"skip:{company.id}"),
            ]
        ]
    )
    try:
        await _send_message(
            chat_id=settings.telegram_chat_id,
            text=text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception as e:
        log.warning(f"Telegram approval request failed: {e}")


async def send_dashboard_receipt(company_name: str, action: str):
    # Normalize action representation (e.g. approve -> approved, reject -> rejected)
    action_clean = action.lower()
    if action_clean == "approve":
        action_clean = "approved"
    elif action_clean == "reject":
        action_clean = "rejected"

    icon = "✅" if action_clean == "approved" else "❌"
    text = f"{icon} {company_name} {action_clean} via Dashboard"

    try:
        await _send_message(
            chat_id=settings.telegram_chat_id,
            text=text,
        )
    except Exception as e:
        log.warning(f"Telegram dashboard receipt failed: {e}")


async def notify_reply(company, reply: dict):
    text = (
        f"\U0001f4ac *Reply received*\n\n*{company.name}* replied to your outreach.\n\n_{reply.get('text', '')[:300]}_"
    )
    try:
        await _send_message(chat_id=settings.telegram_chat_id, text=text, parse_mode="Markdown")
    except Exception as e:
        log.warning(f"Telegram reply notification failed: {e}")


async def send_followup_approval(company, followup_body: str):
    text = (
        f"\U0001f501 *Follow-up ready*\n\n"
        f"No reply from *{company.name}* in 5 days.\n\n"
        f"*Draft follow-up:*\n_{followup_body}_"
    )
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "\u2705 Send follow-up",
                    callback_data=f"followup_approve:{company.id}",
                ),
                InlineKeyboardButton("\u274c Drop it", callback_data=f"followup_skip:{company.id}"),
            ]
        ]
    )
    try:
        await _send_message(
            chat_id=settings.telegram_chat_id,
            text=text,
            reply_markup=keyboard,
            parse_mode="Markdown",
        )
    except Exception as e:
        log.warning(f"Telegram follow-up approval failed: {e}")
