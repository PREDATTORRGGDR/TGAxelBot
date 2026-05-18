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
        f"/dice - бросить кубик\n"
        f"/help - показать cписок команд \n"
        f"/clean - очистить чат"

    )
    bot.send_message(message.chat.id, text)



@bot.message_handler(commands=['coin'])
def cmd_coin(message: Message): 
    result = random.choice(["Орел🦅", "Решка🪙"])
    bot.reply_to(message, f"Выпало: {result}")

@bot.message_handler(commands=['dice'])
def cmd_dice(message: Message):
    resullt = random.randint(1, 6)
    dise_icons = {
        1: "⚀",
        2: "⚁",
        3: "⚂",
        4: "⚃",
        5: "⚄",
        6: "⚅"
    }
    bot.reply_to(message=message, text=f"Выпало: {dise_icons[resullt]} ({resullt})")


@bot.message_handler(commands=['clean'])
def cmd_clean(message: Message):
    chat_id = message.chat.id

    start_id = message.message_id
    end_id = max(start_id - 100, 0)
    for msg_id in range(start_id, end_id, -1):
        try:
            bot.delete_message(chat_id, msg_id)
        except Exception:

            pass

@bot.message_handler(commands=['help'])
def cmd_help(message: Message):
    chat_id = message.chat.id
    text = (
        f"Cписок команд: \n"

    )
    bot.reply_to(message, text)









if __name__ == '__main__':
    # start the bot
    bot.polling(none_stop=True)

