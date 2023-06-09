import os
import time
import sched
import logging
import threading

from time import sleep
from telegram import ChatAction, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler, CommandHandler


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
scheduler = sched.scheduler(time.time, time.sleep)


def start(update, context):
    message = "Hello, I'm a bot that manages your tasks. Try sending me a message and reacting to it!"
    context.bot.send_message(chat_id=update.message.chat_id, text=message)


def last_message_restore(update, context):
    pass


def convert_to_number(message_text):
    try:
        try:
            hours = float(message_text)
            return hours
        except ValueError:
            hours = int(message_text)
            return hours
    except:
        return


def handle_message(update, context):
    message = update.message
    chat_id = message.chat_id

    try:
        context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        keyboard = [[InlineKeyboardButton("🔥", callback_data="fire")]]
        markup = InlineKeyboardMarkup(keyboard)

        if message.text:
            text = message.text
            reply_to = message.reply_to_message

            if reply_to:
                hours = convert_to_number(message.text)
                if hours:
                    now = time.time()
                    scheduled_time = now + hours * 3600

                    scheduler.enterabs(scheduled_time, priority=1, action=send_scheduled_message, argument=((chat_id, reply_to, markup),))
                    threading.Thread(target=scheduler.run).start()
                else:
                    return
            else:
                context.bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
        elif message.caption:
            text = message.caption
        else:
            text = None

        if message.photo:
            context.bot.send_photo(chat_id=chat_id, photo=message.photo[-1].file_id, caption=text, reply_markup=markup)
        elif message.document:
            document = message.document.file_id
            context.bot.send_document(chat_id=chat_id, caption=text, document=document, reply_markup=markup)
        elif message.video:
            video = message.video.file_id
            context.bot.send_video(chat_id=chat_id, caption=text, video=video, reply_markup=markup)
        elif message.audio:
            audio = message.audio.file_id
            context.bot.send_audio(chat_id=chat_id, caption=text, audio=audio, reply_markup=markup)
        elif message.sticker:
            context.bot.send_sticker(chat_id=chat_id, sticker=message.sticker.file_id, reply_markup=markup)
        context.bot.delete_message(message_id=message.message_id, chat_id=chat_id)
    except Exception as ex:
        context.bot.send_message(chat_id=chat_id, text=str(ex))


def send_scheduled_message(context):
    chat_id, message, markup = context
    try:
        updater.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
    except:
        pass

    if message.text:
        updater.bot.send_message(chat_id=chat_id, text=message.text, reply_markup=markup)
    elif message.photo:
        updater.bot.send_photo(chat_id=chat_id, photo=message.photo[-1].file_id, caption=message.text, reply_markup=markup)
    elif message.document:
        document = message.document.file_id
        updater.bot.send_document(chat_id=chat_id, caption=message.caption, document=document, reply_markup=markup)
    elif message.video:
        video = message.video.file_id
        updater.bot.send_video(chat_id=chat_id, caption=message.caption, video=video, reply_markup=markup)
    elif message.audio:
        audio = message.audio.file_id
        updater.bot.send_audio(chat_id=chat_id, caption=message.caption, audio=audio, reply_markup=markup)
    elif message.sticker:
        updater.bot.send_sticker(chat_id=chat_id, sticker=message.sticker.file_id, reply_markup=markup)


def handle_reaction(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    reaction = query.data

    if reaction == "fire":
        context.bot.delete_message(chat_id=chat_id, message_id=message_id)


updater = Updater(token=os.environ.get('TELEGRAM_TOKEN'), use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(Filters.text | Filters.photo | Filters.document | Filters.video | Filters.audio | Filters.sticker, handle_message))
dispatcher.add_handler(CallbackQueryHandler(handle_reaction))
dispatcher.add_handler(CommandHandler("start", start))


while True:
    updater.start_polling()
    sleep(3)
