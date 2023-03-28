from dotenv import load_dotenv
import os
import time
import telebot
from telebot import types

bool = False
load_dotenv()

JumbledWord_Bool = os.environ.get(
    'Temp_JumbledWord_Bool', 'Temp_JumbledWord_Bool')

bot = telebot.TeleBot(os.getenv('API_KEY'))

print("Hi,!\n\t", os.getenv('bot_username'))


@bot.message_handler(commands=['menu'])
def send_menu(message):
    global bool
    if (not bool):
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, row_width=3)

        button1 = types.KeyboardButton(os.getenv('JWB'))
        button2 = types.KeyboardButton(os.getenv('WCB'))
        button3 = types.KeyboardButton(os.getenv('SBB'))
        markup.add(button1, button2, button3)
        bool = True
        markup.one_time_keyboard = True

        bot.send_message(chat_id=message.chat.id,
                         text='/ Welcome to the menu! \\', reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    global bool
    try:
        print(message.text)
        r = ['/jumbleword', '/WCB', '/SBB',
             '/storybuildingbot', '/startclassic', '/menu']
        if (bool):
            if message.text in r:
                bot.send_message(chat_id=message.chat.id,
                                 text='started the Game: '+message.text)
            time.sleep(60)
            bool = False

    except Exception as e:
        print("Error: ", e)


# # Start your bot's polling loop
bot.polling()
