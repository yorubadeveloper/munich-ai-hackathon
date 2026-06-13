"""
Telegram bot handlers.
Listens for button callbacks from approval messages.
Resumes the agent loop on approve.

This module lives in `tg/` (not `telegram/`) so it does not shadow the
installed `python-telegram-bot` package, whose top-level import is `telegram`.
"""
import asyncio
import logging

from telegram.ext import Application, CallbackQueryHandler
from sqlalchemy import select

from agents.orchestrator import run_pipeline
from agents.delivery import send as delivery_send  # noqa: F401  (kept for parity)
from models import Company, Message
from database import AsyncSessionLocal
from config import settings

log = logging.getLogger(__name__)


async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("approve:"):
        company_id = data.split(":")[1]
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
        await query.edit_message_text("\u2705 Approved. Sending now...")

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


async def start_bot():
    if not settings.telegram_bot_token:
        log.warning("TELEGRAM_BOT_TOKEN not set — Telegram bot disabled.")
        return
    try:
        app = Application.builder().token(settings.telegram_bot_token).build()
        app.add_handler(CallbackQueryHandler(handle_callback))
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        log.info("Telegram bot started and polling for callbacks.")
    except Exception as e:
        log.warning(f"Telegram bot failed to start: {e}")
