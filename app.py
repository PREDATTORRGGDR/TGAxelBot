import telebot, random
from telebot.types import Message
bot = telebot.TeleBot('8910131268:AAHxGzYIkzkuO_KAE5Po2M-rEBz6hkpez5I')

@bot.message_handler(commands=['start'])
def cmd_start(message: Message):
    user_name = message.from_user.username
    text = (
        f"Привет {user_name}! \n"
        f"Я - бот и меня зовут Майк Вазовский👋\n"
        f"/coin - бросить монету\n"
        f"\n"
        f"/help - показать cписок команд"

    )
    bot.send_message(message.chat.id, text)



@bot.message_handler(commands=['coin'])
def cmd_coin(message: Message): 
    result = random.choice(["Орел🦅", "Решка🪙"])
    bot.reply_to(message, f"Выпало: {result}")

if __name__ == '__main__':
    # start the bot
    bot.polling(none_stop=True)

