import telebot
from telebot import types
import os

# Получение токена из переменной окружения
API_TOKEN = os.getenv("BOT_TOKEN")  # НЕ ХРАНИ ТОКЕН В КОДЕ!

if not API_TOKEN:
    raise ValueError("Токен бота не найден! Установи переменную окружения BOT_TOKEN.")

bot = telebot.TeleBot(API_TOKEN)

user_data = {}

def reset_user(uid):
    user_data[uid] = {
        "step": "start",
        "platform": None,
        "amount": None,
        "login": None
    }

def kb_start():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🚀 Начать")
    return kb

def kb_platform():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Steam", "Epic Games")
    kb.add("🔙 Назад")
    return kb

def kb_amount():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("100", "500", "1000", "2000")
    kb.add("🔙 Назад")
    return kb

def kb_back():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🔙 Назад")
    return kb

def kb_confirm():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Подтвердить")
    kb.add("🔙 Назад")
    return kb

@bot.message_handler(commands=['start'])
def cmd_start(msg):
    uid = msg.chat.id
    reset_user(uid)
    bot.send_message(uid,
        "Привет! 👋\n"
        "Я бот для донатов на Steam и Epic Games.\n"
        "Нажми «Начать», чтобы продолжить.",
        reply_markup=kb_start()
    )

@bot.message_handler(func=lambda m: True)
def handle(msg):
    uid = msg.chat.id
    text = msg.text

    if uid not in user_data:
        reset_user(uid)

    step = user_data[uid]["step"]

    if text == "🔙 Назад":
        return go_back(uid)

    if step == "start":
        if text == "🚀 Начать":
            user_data[uid]["step"] = "choose_platform"
            bot.send_message(uid, "Выбери платформу:", reply_markup=kb_platform())
        else:
            bot.send_message(uid, "Нажми кнопку «Начать».")
        return

    if step == "choose_platform":
        if text in ["Steam", "Epic Games"]:
            user_data[uid]["platform"] = text
            user_data[uid]["step"] = "choose_amount"
            bot.send_message(uid, f"Платформа выбрана: {text}\nТеперь выбери сумму:", reply_markup=kb_amount())
        else:
            bot.send_message(uid, "Выберите платформу кнопками.")
        return

    if step == "choose_amount":
        if text.isdigit():
            user_data[uid]["amount"] = int(text)
            user_data[uid]["step"] = "enter_login"
            bot.send_message(uid, "Введите логин (только латиница):", reply_markup=kb_back())
        else:
            bot.send_message(uid, "Выберите сумму кнопками.")
        return

    if step == "enter_login":
        if not text.isascii():
            bot.send_message(uid, "Ошибка: логин должен быть на английском!", reply_markup=kb_back())
            return

        user_data[uid]["login"] = text
        user_data[uid]["step"] = "confirm"

        bot.send_message(uid,
            f"Проверь данные:\n\n"
            f"Платформа: {user_data[uid]['platform']}\n"
            f"Сумма: {user_data[uid]['amount']} руб.\n"
            f"Логин: {user_data[uid]['login']}\n\n"
            f"Если всё верно — подтверждай.",
            reply_markup=kb_confirm()
        )
        return

    if step == "confirm":
        if text == "Подтвердить":
            bot.send_message(uid,
                "💳 Выполняю перевод...\n"
                "✔ Донат успешно отправлен!",
                reply_markup=kb_start()
            )
            reset_user(uid)
        else:
            bot.send_message(uid, "Нажмите «Подтвердить» или «Назад».")
        return

def go_back(uid):
    step = user_data[uid]["step"]

    if step == "choose_platform":
        reset_user(uid)
        bot.send_message(uid, "Начало. Нажми «Начать».", reply_markup=kb_start())
        return

    if step == "choose_amount":
        user_data[uid]["step"] = "choose_platform"
        bot.send_message(uid, "Выбери платформу:", reply_markup=kb_platform())
        return

    if step == "enter_login":
        user_data[uid]["step"] = "choose_amount"
        bot.send_message(uid, "Выбери сумму:", reply_markup=kb_amount())
        return

    if step == "confirm":
        user_data[uid]["step"] = "enter_login"
        bot.send_message(uid, "Введите логин:", reply_markup=kb_back())
        return

bot.polling(none_stop=True)
