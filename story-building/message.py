import telebot

from main import bot


def send_join_prompt(chat_id, time):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton(
            'Join Game 🎮', callback_data='join-game'),
    )

    bot.send_message(
        chat_id, f'*{time}*sec left to join the game.',
        reply_markup=keyboard,
        parse_mode='markdown'
    )


def send_start_message(chat_id, first_name):
    bot.send_message(chat_id, f'{first_name} started the game.')


def send_join_message(chat_id, first_name):
    bot.send_message(chat_id, f'{first_name} joined the game.')


def send_false_start_message(chat_id):
    bot.send_message(chat_id, 'Not enough players!')


def send_game_prompt(chat_id, first_sentence):
    bot.send_message(chat_id, f'Game is starting.\nBuild a story with first line as -\n{first_sentence}')


def send_turn_prompt(chat_id, first_name, turn_time):
    bot.send_message(chat_id, f'{first_name}\'s turn, {turn_time}s to answer')


def send_skip_turn_message(chat_id, first_name):
    bot.send_message(chat_id, f'{first_name} ran out of time')


def send_story_sentence(chat_id, text, corrected_text):
    if text.casefold() != corrected_text.casefold():
        bot.send_message(chat_id, text + ' ❗')
        bot.send_message(chat_id, f'Correct response - {corrected_text}')
    else:
        bot.send_message(chat_id, text + ' ✅')


def send_story(chat_id, story):
    bot.send_message(chat_id, f'Well played everyone, here is the story that we created.\n{story}')
