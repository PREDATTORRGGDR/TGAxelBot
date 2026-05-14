import telebot
from telebot.types import Message
bot = telebot.TeleBot('8910131268:AAHxGzYIkzkuO_KAE5Po2M-rEBz6hkpez5I')

@bot.message_handler(commands=['start'])
def cmd_start(message: Message):
    user_name = message.from_user.username
    text = (
        f"Привет {user_name}! \n"
        f"Я - бот и меня зовут Майк Вазовский."
    )
    bot.send_message(message.chat.id, text)

bot.polling()

