from dotenv import load_dotenv
import os
import telebot
from telebot import types

load_dotenv()
# run = True

bot = telebot.TeleBot(os.getenv('API_KEY'))


print("Hi,!\n\t", os.getenv('bot_username'))


@bot.message_handler(commands=['menu'])
def send_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=3)

    button1 = telebot.types.KeyboardButton(os.getenv('JWB'))
    button2 = telebot.types.KeyboardButton(os.getenv('WCB'))
    button3 = telebot.types.KeyboardButton(os.getenv('SBB'))

    markup.add(button1, button2, button3)

    markup.one_time_keyboard = True

    bot.send_message(chat_id=message.chat.id,
                     text='/ Welcome to the menu! \\', reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    # if '/menu'
    try:
        # global run
        # print('Run: ', run)
        print(message.text)
        r = ['/jumbleword', '/WCB', '/SBB',
             '/storybuildingbot', '/startclassic', '/menu']
        if message.text in r:
            # print('running')
            # run = False
            bot.send_message(chat_id=message.chat.id,
                             text='started the Game: '+message.text, reply_markup=telebot.types.ReplyKeyboardRemove())
        # elif not run:
        #     bot.send_message(chat_id=message.chat.id,
        #                      text='Game is already started.', reply_markup=telebot.types.ReplyKeyboardRemove())
        # else:
        #     run = True
    except Exception as e:
        print("Error: ", e)


# # Start your bot's polling loop
bot.polling()
