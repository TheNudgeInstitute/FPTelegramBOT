from dotenv import load_dotenv
import os
import telebot
from telebot import types

load_dotenv()

bot = telebot.TeleBot(os.getenv('API_KEY'))

start_command = types.BotCommand(
    command="/start_i_added_it", description="Start the bot")
runn_command = types.BotCommand(command="/run", description="Run a task")

# Set the bot's commands to the list of commands
bot.set_my_commands([start_command, runn_command])
print("Hi, Jumble here!\n\t", os.getenv('bot_username'))


@bot.message_handler(commands=['menu'])
def send_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=3)

    button1 = telebot.types.KeyboardButton('/jumbleword')
    button2 = telebot.types.KeyboardButton('/QB')
    button3 = telebot.types.KeyboardButton('/WCB')
    button4 = telebot.types.KeyboardButton('/STG')

    markup.add(button1, button2, button3)
    markup.add(button4)

    markup.one_time_keyboard = True

    bot.send_message(chat_id=message.chat.id,
                     text='/ Welcome to the menu! \\', reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print(message.text)
    r = ['/jumbleword', '/QB', '/WCB', '/STG']
    if message.text in r:
        bot.send_message(chat_id=message.chat.id,
                         text='started the Game: '+message.text, reply_markup=telebot.types.ReplyKeyboardRemove())


# # Start your bot's polling loop
bot.polling()
