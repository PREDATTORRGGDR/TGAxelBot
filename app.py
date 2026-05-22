import random
import os
from dotenv import load_dotenv
import telebot

load_dotenv()
from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in .env")

bot = telebot.TeleBot(BOT_TOKEN)

STORIES = [
    "Ты лёг спать и почувствовал, что кто-то смотрит на тебя из угла комнаты. Ты закрыл глаза. Утром на полу был чужой след 👁️",
    "Твой телефон прислал тебе сообщение. Ты его не отправлял. Там было только одно слово: 'беги' 📱",
    "Ты считал людей в лифте. Зашло трое. Вышло четверо 🚪",
    "Ночью ты проснулся от смеха ребёнка. Детей в доме нет уже 10 лет 🏚️",
    "Ты смотрел в зеркало. Отражение моргнуло на секунду позже тебя 🪞",
]

CURSES = [
    "Отныне каждый раз когда ты ешь суп — ложка будет падать 🥄",
    "Твои наушники будут запутываться даже в кармане 🎧",
    "Ты будешь просыпаться за 5 минут до будильника навсегда ⏰",
    "Каждый твой зарядный кабель переломится ровно посередине ⚡",
    "Ты будешь вспоминать неловкие моменты из прошлого каждую ночь 😶",
]

GHOST_FACTS = [
    "В Японии считают, что духи умерших возвращаются домой раз в год в августе 🏮",
    "По статистике, большинство людей 'чувствовали присутствие' кого-то в пустой комнате 👤",
    "Инфразвук на частоте 18 Гц вызывает у людей чувство тревоги и ощущение призраков 🔊",
    "В Великобритании официально зарегистрировано более 10 000 'населённых призраками' мест 🏰",
    "Учёные выяснили, что мозг продолжает слышать после смерти тела ещё несколько минут 🧠",
]


@bot.message_handler(commands=["start"])
def cmd_start(message: Message):
    user_name = message.from_user.username or message.from_user.first_name or "друг"
    text = (
        f"Привет, {user_name}...\n"
        "Я Майк Вазовский 👁️\n"
        "Я вижу тебя. Выбери, что тебе нужно."
    )
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton(text="Напугай 👻", callback_data="scare"),
        InlineKeyboardButton(text="Прокляни 😈", callback_data="curse"),
    )
    kb.row(
        InlineKeyboardButton(text="Паранормальное 👁️", callback_data="ghost"),
        InlineKeyboardButton(text="Помощь", callback_data="help"),
    )
    track(message.chat.id, bot.send_message(message.chat.id, text, reply_markup=kb))


@bot.message_handler(commands=["scare"])
def cmd_scare(message: Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="Напугай ещё 👻", callback_data="scare"))
    track(message.chat.id, bot.reply_to(message, random.choice(STORIES), reply_markup=kb))


@bot.message_handler(commands=["curse"])
def cmd_curse(message: Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="Прокляни ещё 😈", callback_data="curse"))
    track(message.chat.id, bot.reply_to(message, random.choice(CURSES), reply_markup=kb))


@bot.message_handler(commands=["ghost"])
def cmd_ghost(message: Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="Ещё факт 👁️", callback_data="ghost"))
    track(message.chat.id, bot.reply_to(message, random.choice(GHOST_FACTS), reply_markup=kb))


bot_message_ids: dict[int, list[int]] = {}


def track(chat_id: int, msg: Message):
    bot_message_ids.setdefault(chat_id, []).append(msg.message_id)


@bot.message_handler(commands=["clean"])
def cmd_clean(message: Message):
    chat_id = message.chat.id
    for mid in bot_message_ids.get(chat_id, []):
        try:
            bot.delete_message(chat_id, mid)
        except Exception:
            pass
    bot_message_ids[chat_id] = []
    try:
        bot.delete_message(chat_id, message.message_id)
    except Exception:
        pass
    cmd_start(message)


@bot.message_handler(commands=["help"])
def cmd_help(message: Message):
    text = "Список команд:\n/start\n/scare\n/curse\n/ghost\n/info\n/help\n/clean"
    track(message.chat.id, bot.reply_to(message, text))


@bot.message_handler(commands=["info"])
def cmd_info(message: Message):
    text = "Я Майк Вазовский, создан @kyrapyto 👁️\nРепозиторий: https://github.com/PREDATTORRGGDR/TGAxelBot"
    track(message.chat.id, bot.reply_to(message, text))


@bot.callback_query_handler(func=lambda call: True)
def on_callback(call: CallbackQuery):
    handlers = {
        "scare": cmd_scare,
        "curse": cmd_curse,
        "ghost": cmd_ghost,
        "help": cmd_help,
    }
    if call.data in handlers:
        handlers[call.data](call.message)
    bot.answer_callback_query(call.id)


if __name__ == "__main__":
    bot.polling(none_stop=True)
