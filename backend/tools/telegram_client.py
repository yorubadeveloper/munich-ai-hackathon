"""
Telegram outbound helpers — approval requests, reply notifications, follow-ups.
These send messages with inline keyboards; the callbacks are handled in tg/bot.py.
"""
import logging

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from config import settings

log = logging.getLogger(__name__)

bot = Bot(token=settings.telegram_bot_token) if settings.telegram_bot_token else None


async def _send_message(**kwargs):
    if bot is None or not settings.telegram_chat_id:
        log.warning("Telegram credentials not set - skipping outbound message.")
        return
    await bot.send_message(**kwargs)


async def send_approval_request(company, draft):
    score = company.fit_score or 0
    text = (
        f"\U0001F3AF *New match ready*\n\n"
        f"*{company.name}*\n"
        f"Fit score: {score:.1f}/10\n"
        f"Channel: {'LinkedIn DM' if draft.channel == 'linkedin' else 'Email'}\n\n"
        f"*Draft:*\n_{draft.body[:400]}_"
    )
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "\u2705 Send it", callback_data=f"approve:{company.id}"
                ),
                InlineKeyboardButton(
                    "\u274C Skip", callback_data=f"skip:{company.id}"
                ),
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
        log.warning(f"Telegram approval request failed: {e}")


async def notify_reply(company, reply: dict):
    text = (
        f"\U0001F4AC *Reply received*\n\n"
        f"*{company.name}* replied to your outreach.\n\n"
        f"_{reply.get('text', '')[:300]}_"
    )
    try:
        await _send_message(
            chat_id=settings.telegram_chat_id, text=text, parse_mode="Markdown"
        )
    except Exception as e:
        log.warning(f"Telegram reply notification failed: {e}")


async def send_followup_approval(company, followup_body: str):
    text = (
        f"\U0001F501 *Follow-up ready*\n\n"
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
                InlineKeyboardButton(
                    "\u274C Drop it", callback_data=f"followup_skip:{company.id}"
                ),
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
