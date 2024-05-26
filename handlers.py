from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from config import CRYPTS, ACTIONS, BOT_TOKEN, SHORT_ACTIONS
from models import User
import telegram
import json


bot = telegram.Bot(token=BOT_TOKEN)


async def start_command(update, context) -> None:
    keyboard = [
        [
            InlineKeyboardButton("₿ Криптовалюта", callback_data="crypto"),
            InlineKeyboardButton("🧾 Акции", callback_data="actions"),
        ],
        [
            InlineKeyboardButton("📈 Прогноз", callback_data="predict"),
        ],
        [
            InlineKeyboardButton("Помощь авторам", callback_data="support_authors"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_html(
        "<b>Привет!</b>\n\nЭтот бот поможет вам отлеживать аномалии котировок акций и криптовалют\n\n\
Выберите активы, которые вы хотели бы отслеживать",
        reply_markup=reply_markup
    )


async def button(update, context) -> None:
    query = update.callback_query

    await query.answer()

    if query.data == "crypto":
        user = User.select().where(User.user_id == update.effective_user.id)
        if not user.exists():
            User.create(user_id=update.effective_user.id, crypts="", actions="")
        user = user.get()

        keyboard = [[InlineKeyboardButton(("✅" if CRYPTS[j + i * 3] + ',' in user.crypts else "") + CRYPTS[j + i * 3],
                                          callback_data=CRYPTS[j + i * 3]) for j in range(3)] for i in range(4)]

        keyboard.append([InlineKeyboardButton("Назад", callback_data="start")])
        text = "Выберите криптовалюту:"

    if query.data == "actions":
        user = User.select().where(User.user_id == update.effective_user.id)
        if not user.exists():
            User.create(user_id=update.effective_user.id, crypts="", actions="")
        user = user.get()

        keyboard = [[InlineKeyboardButton(("✅" if ACTIONS[j + i * 3] + ',' in user.actions else "") + ACTIONS[j + i * 3],
                                          callback_data=ACTIONS[j + i * 3]) for j in range(3)] for i in range(6)]

        keyboard.append([InlineKeyboardButton("Назад", callback_data="start")])
        text = "Выберите акции:"

    elif query.data == "start":
        keyboard = [
            [
                InlineKeyboardButton("₿ Криптовалюта", callback_data="crypto"),
                InlineKeyboardButton("🧾 Акции", callback_data="actions"),
            ],
            [
                InlineKeyboardButton("📈 Прогноз", callback_data="predict"),
            ],
            [
                InlineKeyboardButton("Помощь авторам", callback_data="support_authors"),
            ]
        ]
        text = "Выберите активы, которые вы хотели бы отслеживать:"

    elif query.data in CRYPTS:
        crypto = query.data
        user = User.get(User.user_id == update.effective_user.id)
        if crypto in user.crypts:
            user.crypts = user.crypts.replace(crypto + ",", "")
        else:
            user.crypts += crypto + ","
        user.save()
        keyboard = [[InlineKeyboardButton(("✅" if CRYPTS[j + i * 3] + ',' in user.crypts else "") + CRYPTS[j + i * 3],
                                          callback_data=CRYPTS[j + i * 3]) for j in range(3)] for i in range(4)]

        keyboard.append([InlineKeyboardButton("Назад", callback_data="start")])
        text = "Выберите криптовалюту:"

    elif query.data in ACTIONS:
        action = query.data
        user = User.get(User.user_id == update.effective_user.id)
        if action in user.actions:
            user.actions = user.actions.replace(action + ",", "")
        else:
            user.actions += action + ","
        user.save()
        keyboard = [[InlineKeyboardButton(("✅" if ACTIONS[j + i * 3] + ',' in user.actions else "") + ACTIONS[j + i * 3],
                                          callback_data=ACTIONS[j + i * 3]) for j in range(3)] for i in range(6)]

        keyboard.append([InlineKeyboardButton("Назад", callback_data="start")])
        text = "Выберите акции:"

    elif query.data == "predict":
        user = User.get(User.user_id == update.effective_user.id)
        keyboard = [[InlineKeyboardButton("Назад", callback_data="start")]]
        text = "<b>Прогноз цены на отслеживаемые активы</b>"
        with open('predict.json') as file:
            data = json.load(file)
        for active in (user.crypts + user.actions).split(","):
            predict_price = data.get(active, 0)
            if predict_price:
                text += f"\n\n<b>{active}:</b>\nHigh: {predict_price['High']}\nLow: {predict_price['Low']}"

    elif query.data == "support_authors":
        keyboard = [
            [InlineKeyboardButton("Перейти к оплате", url="https://t.me/send?start=IVQWq1Vh4f8k")],
            [InlineKeyboardButton("Назад", callback_data="start")]
        ]
        text = "<b>Нажмите для пожертвования👇</b>"

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=telegram.constants.ParseMode.HTML)
