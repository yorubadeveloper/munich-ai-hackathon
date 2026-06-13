"""
Telegram bot handlers.
Listens for button callbacks from approval messages and resumes the agent loop
on approve. Also supports editing a draft before sending:

    [Send it] [Edit] [Skip]
      Edit -> bot asks for new text -> you type it -> [Send edited] [Cancel]

This module lives in `tg/` (not `telegram/`) so it does not shadow the
installed `python-telegram-bot` package, whose top-level import is `telegram`.
"""
import asyncio
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from sqlalchemy import select

from agents.orchestrator import run_pipeline
from models import Company, Message
from database import AsyncSessionLocal
from config import settings

log = logging.getLogger(__name__)

# Per-chat "awaiting edited draft for company X" state.
# chat_id -> company_id
_pending_edits: dict[int, str] = {}


async def _approve_and_send(company_id: str):
    async with AsyncSessionLocal() as db:
        company = await db.get(Company, company_id)
        msg_result = await db.execute(
            select(Message).where(
                Message.company_id == company_id, Message.status == "pending"
            )
        )
        message = msg_result.scalar_one_or_none()
        if message and company:
            message.status = "approved"
            company.status = "approved"
            await db.commit()
    asyncio.create_task(run_pipeline(company_id))


async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("approve:"):
        company_id = data.split(":")[1]
        await _approve_and_send(company_id)
        await query.edit_message_text("\u2705 Approved. Sending now...")

    elif data.startswith("edit:"):
        company_id = data.split(":")[1]
        chat_id = query.message.chat_id
        _pending_edits[chat_id] = company_id
        await query.edit_message_text(
            query.message.text
            + "\n\n\u270F\uFE0F *Send me the edited message text now.*"
            "\nIt will replace the draft. Send /cancel to abort.",
            parse_mode=ParseMode.MARKDOWN,
        )

    elif data.startswith("send_edited:"):
        company_id = data.split(":")[1]
        await _approve_and_send(company_id)
        await query.edit_message_text("\u2705 Edited message approved. Sending now...")

    elif data.startswith("cancel_edit:"):
        company_id = data.split(":")[1]
        _pending_edits.pop(query.message.chat_id, None)
        await query.edit_message_text("Edit cancelled. Draft left as-is, not sent.")

    elif data.startswith("skip:"):
        company_id = data.split(":")[1]
        async with AsyncSessionLocal() as db:
            company = await db.get(Company, company_id)
            if company:
                company.status = "skipped_by_user"
                await db.commit()
        await query.edit_message_text("\u274C Skipped.")

    elif data.startswith("followup_approve:"):
        company_id = data.split(":")[1]
        async with AsyncSessionLocal() as db:
            msg_result = await db.execute(
                select(Message).where(
                    Message.company_id == company_id, Message.status == "sent"
                )
            )
            message = msg_result.scalar_one_or_none()
            if message:
                message.followup_status = "approved"
                await db.commit()
        await query.edit_message_text("\u2705 Follow-up approved. Sending...")

    elif data.startswith("followup_skip:"):
        company_id = data.split(":")[1]
        async with AsyncSessionLocal() as db:
            msg_result = await db.execute(
                select(Message).where(
                    Message.company_id == company_id, Message.status == "sent"
                )
            )
            message = msg_result.scalar_one_or_none()
            if message:
                message.followup_status = "skipped"
                await db.commit()
        await query.edit_message_text("Dropped.")


async def handle_text(update, context):
    """Capture an edited draft when the user is in 'awaiting edit' state."""
    if not update.message or not update.message.text:
        return
    chat_id = update.message.chat_id

    if update.message.text.strip() == "/cancel":
        _pending_edits.pop(chat_id, None)
        await update.message.reply_text("Edit cancelled.")
        return

    company_id = _pending_edits.get(chat_id)
    if not company_id:
        return  # not editing anything; ignore

    new_text = update.message.text.strip()
    async with AsyncSessionLocal() as db:
        msg_result = await db.execute(
            select(Message).where(
                Message.company_id == company_id, Message.status == "pending"
            )
        )
        message = msg_result.scalar_one_or_none()
        if message:
            message.final_body = new_text
            await db.commit()

    _pending_edits.pop(chat_id, None)

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "\u2705 Send edited", callback_data=f"send_edited:{company_id}"
                ),
                InlineKeyboardButton(
                    "\u274C Cancel", callback_data=f"cancel_edit:{company_id}"
                ),
            ]
        ]
    )
    await update.message.reply_text(
        "Here is your edited message:\n\n" + new_text + "\n\nSend it?",
        reply_markup=keyboard,
    )


async def start_bot():
    if not settings.telegram_bot_token:
        log.warning("TELEGRAM_BOT_TOKEN not set — Telegram bot disabled.")
        return
    try:
        app = Application.builder().token(settings.telegram_bot_token).build()
        app.add_handler(CallbackQueryHandler(handle_callback))
        app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
        )
        # /cancel still needs to reach handle_text:
        app.add_handler(MessageHandler(filters.Regex(r"^/cancel$"), handle_text))
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        log.info("Telegram bot started and polling for callbacks.")
    except Exception as e:
        log.warning(f"Telegram bot failed to start: {e}")
