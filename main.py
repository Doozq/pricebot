import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, Updater
from peewee import *
from config import BOT_TOKEN, CRYPTS, ACTIONS, SHORT_ACTIONS
from handlers import start_command, button
from models import User
from function import get_changes_as_string
import threading
import time
from bd_for_neiro import get_top_20_stocks
import datetime as dt


db = SqliteDatabase('db.db')
db.connect()

bot = telegram.Bot(token=BOT_TOKEN)


def run_periodic_task(application):
    get_changes_as_string()
    time.sleep(35)
    while True:
        changes = get_changes_as_string()
        application.job_queue.run_once(lambda context: notification(context.application, changes), 0)
        time.sleep(40)


def run_periodic_task2():
    while True:
        now = dt.datetime.now()
        if now.hour == 0 and now.minute <= 5:
            get_top_20_stocks()
        time.sleep(290)


async def notification(application, changes):
    for key in changes:
        if key in CRYPTS:
            users = User.select().where(User.crypts.contains(key + ","))
        elif key in ACTIONS:
            users = User.select().where(User.actions.contains(key + ","))
        text = changes[key]
        for user in users:
            try:
                await application.bot.send_message(chat_id=user.user_id, text=text, parse_mode=telegram.constants.ParseMode.HTML)
            except telegram.error.TimedOut:
                pass
            except telegram.error.TimedOut:
                pass


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button))
    periodic_thread = threading.Thread(target=run_periodic_task, args=(application,))
    periodic_thread.start()
    periodic_thread2 = threading.Thread(target=run_periodic_task2)
    periodic_thread2.start()
    application.run_polling()


if __name__ == '__main__':
    main()
