#!/usr/bin/env python3
import logging
import json
import os
import nest_asyncio
import asyncio

# Применяем nest_asyncio для поддержки вложенных циклов событий
nest-asyncio.apply()

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

GROUPS_FILE = 'groups.json'

if os.path.exists(GROUPS_FILE):
    with open(GROUPS_FILE, 'r') as f:
        group_ids = json.load(f)
else:
    group_ids = []

def save_groups():
    with open(GROUPS_FILE, 'w') as f:
        json.dump(group_ids, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь сообщение в личном чате, и я перешлю его в группы.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type in ["group", "supergroup"]:
        if chat.id not in group_ids:
            group_ids.append(chat.id)
            save_groups()
            logger.info(f"Группа добавлена: {chat.id}")
    elif chat.type == "private":
        message_text = update.message.text
        for group_id in group_ids:
            try:
                await context.bot.send_message(chat_id=group_id, text=message_text)
            except Exception as e:
                logger.error(f"Ошибка отправки в группу {group_id}: {e}")

async def main():
    TOKEN = "YOUR_BOT_TOKEN_HERE"  # Замени на токен своего бота
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
