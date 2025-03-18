#!/usr/bin/env python3
import logging
import json
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Файл для хранения ID групп
GROUPS_FILE = 'groups.json'

# Загружаем ID групп из файла, если он существует
if os.path.exists(GROUPS_FILE):
    with open(GROUPS_FILE, 'r') as f:
        group_ids = json.load(f)
else:
    group_ids = []

def save_groups():
    with open(GROUPS_FILE, 'w') as f:
        json.dump(group_ids, f)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Отправь мне сообщение в личном чате, и я перешлю его во все группы, где я добавлен.")

def handle_message(update: Update, context: CallbackContext):
    chat = update.effective_chat

    # Если сообщение пришло из группы – регистрируем группу (если еще не добавлена)
    if chat.type in ["group", "supergroup"]:
        if chat.id not in group_ids:
            group_ids.append(chat.id)
            save_groups()
            logger.info(f"Добавлена группа: {chat.id}")
    # Если сообщение пришло в личном чате – пересылаем его во все сохраненные группы
    elif chat.type == "private":
        message_text = update.message.text
        for group_id in group_ids:
            try:
                context.bot.send_message(chat_id=group_id, text=message_text)
            except Exception as e:
                logger.error(f"Ошибка отправки в группу {group_id}: {e}")

def main():
    TOKEN = "YOUR_BOT_TOKEN_HERE"  # Замени на токен своего бота
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
