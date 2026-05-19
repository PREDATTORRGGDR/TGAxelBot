import random
import os
import telebot
from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN: #Токен я поменял XD
    raise RuntimeError("BOT_TOKEN is not set")

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start"])
def cmd_start(message: Message):
    user_name = message.from_user.username or message.from_user.first_name or "друг"
    text = (
        f"Привет, {user_name}!\n"
        "Я бот, меня зовут Майк Вазовский 👋\n"
        "Выбери действие кнопкой ниже."
    )

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton(text="Информация", callback_data="info"),
        InlineKeyboardButton(text="Помощь", callback_data="help"),
    )
    kb.row(
        InlineKeyboardButton(text="Монета", callback_data="coin"),
        InlineKeyboardButton(text="Кубик", callback_data="dice"),
    )
    bot.send_message(message.chat.id, text, reply_markup=kb)


@bot.message_handler(commands=["coin"])
def cmd_coin(message: Message):
    result = random.choice(["Орел 🦅", "Решка 🪙"])
    bot.reply_to(message, f"Выпало: {result}")


@bot.message_handler(commands=["dice"])
def cmd_dice(message: Message):
    result = random.randint(1, 6)
    dice_icons = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
    bot.reply_to(message, f"Выпало: {dice_icons[result]} ({result})")


@bot.message_handler(commands=["clean"])
def cmd_clean(message: Message):
    chat_id = message.chat.id
    start_id = message.message_id
    end_id = max(start_id - 100, 0)
    for msg_id in range(start_id, end_id, -1):
        try:
            bot.delete_message(chat_id, msg_id)
        except Exception:
            pass


@bot.message_handler(commands=["help"])
def cmd_help(message: Message):
    text = "Список команд:\n/start\n/info\n/coin\n/dice\n/help\n/clean"
    bot.reply_to(message, text)


@bot.message_handler(commands=["info"])
def cmd_info(message: Message):
    text = "Я бот, созданный @kyrapyto. Репозиторий: https://github.com/PREDATTORRGGDR/TGAxelBot"
    bot.reply_to(message, text)


@bot.callback_query_handler(func=lambda call: True)
def on_callback(call: CallbackQuery):
    if call.data == "info":
        cmd_info(call.message)
    elif call.data == "help":
        cmd_help(call.message)
    elif call.data == "coin":
        cmd_coin(call.message)
    elif call.data == "dice":
        cmd_dice(call.message)

    bot.answer_callback_query(call.id)


if __name__ == "__main__":
    bot.polling(none_stop=True)
