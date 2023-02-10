import os
import random
import sys
import threading
import time
import traceback

import telebot
from dotenv import load_dotenv

import utils
from check import grammar_check
from utils import get_current_user_name, get_current_user_id

load_dotenv()

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

import common
import timer
from message import send_start_message, send_join_message, send_false_start_message, send_turn_prompt, \
    send_skip_turn_message, send_game_prompt, send_story_sentence, send_story


def end_game(chat_id):
    if not common.IS_ACTIVE:
        return
    common.IS_ACTIVE = False
    common.STARTED = False
    common.CURRENT_PARTICIPANT_INDEX = None
    common.ROUND = 0
    common.PARTICIPANT_MAP = {}
    common.PARTICIPANTS = []
    if common.STORY:
        print(common.STORY)
        if len(common.STORY) > 1:
            send_story(chat_id, "\n".join(common.STORY))
        else:
            send_false_start_message(chat_id)
        common.STORY = []
    print('=== GAME END ===')


def next_turn(chat_id):
    # Last participant in round
    if common.CURRENT_PARTICIPANT_INDEX == len(common.PARTICIPANTS) - 1:
        if common.ROUND == common.MAX_ROUNDS:
            end_game(chat_id)
            return
        else:
            common.ROUND += 1
            common.CURRENT_PARTICIPANT_INDEX = 0
    else:
        common.CURRENT_PARTICIPANT_INDEX += 1
    print(f'Round: {common.ROUND}\tUser: {utils.get_current_user_name()}')

    send_turn_prompt(chat_id, get_current_user_name(), common.TURN_TIME_LIMIT)

    answer_timer_thread = threading.Thread(target=timer.answer_timer,
                                           args=[get_current_user_id(),
                                                 common.ROUND,
                                                 chat_id,
                                                 common.TURN_TIME_LIMIT])
    answer_timer_thread.start()


def skip_turn(chat_id):
    print(f'Round: {common.ROUND}\tUser: {utils.get_current_user_name()}\tSkipped')
    send_skip_turn_message(chat_id, get_current_user_name())
    next_turn(chat_id)


def play_turn(message):
    # TODO Disable Getting Messages During Play Turn
    print(f'Round: {common.ROUND}\tUser: {utils.get_current_user_name()}\tMessage: {message.text}')
    corrected_text = grammar_check(message.text)
    if message.from_user.id == get_current_user_id():
        send_story_sentence(message.chat.id, message.text, corrected_text)
        common.STORY.append(corrected_text)
        next_turn(message.chat.id)


def create_game(message):
    print(f'Round: {common.ROUND}\tUser: {message.from_user.first_name}\tCreate')
    chat_id = message.chat.id
    common.IS_ACTIVE = True
    common.JOIN_MODE = True
    common.PARTICIPANT_MAP[message.from_user.id] = message.from_user.first_name
    common.PARTICIPANTS.append(message.from_user.id)
    send_start_message(chat_id, message.from_user.first_name)

    join_timer_thread = threading.Thread(target=timer.start_join_timer,
                                         args=[chat_id])
    join_timer_thread.start()


def join_game(option):
    if option.from_user.id in common.PARTICIPANT_MAP:
        # TODO Add Handler for Already Joined User
        return
    print(f'Round: {common.ROUND}\tUser: {option.from_user.first_name}\tJoin')
    common.PARTICIPANT_MAP[option.from_user.id] = option.from_user.first_name
    common.PARTICIPANTS.append(option.from_user.id)

    send_join_message(option.message.chat.id, option.from_user.first_name)

    if len(common.PARTICIPANTS) == common.MAX_PARTICIPANTS:
        common.JOIN_MODE = False
        if not common.STARTED:
            common.STARTED = True
            start_game(option.message.chat.id)


def start_game(chat_id):
    if len(common.PARTICIPANTS) < common.MIN_PARTICIPANTS:
        send_false_start_message(chat_id)
        common.JOIN_MODE = False
        utils.publish_game_data(False)
        end_game(None)
        return
    # Start Game
    common.JOIN_MODE = False
    utils.publish_game_data(True)
    time.sleep(5)  # To allow join messages to complete
    print('=== GAME START ===')
    common.CURRENT_PARTICIPANT_INDEX = 0
    common.ROUND = 1
    first_sentence = random.choice(common.PROMPTS)
    send_game_prompt(chat_id, first_sentence)
    common.STORY.append(first_sentence)
    send_turn_prompt(chat_id, get_current_user_name(), common.TURN_TIME_LIMIT)

    answer_timer_thread = threading.Thread(target=timer.answer_timer,
                                           args=[get_current_user_id(),
                                                 common.ROUND,
                                                 chat_id,
                                                 common.TURN_TIME_LIMIT])
    answer_timer_thread.start()


def main():
    @bot.message_handler(commands=['startstorybuilding'])
    def send_welcome(message):
        if not common.IS_ACTIVE:
            create_game(message)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(option):
        if option.data == 'join-game' and common.JOIN_MODE:
            join_game(option)

    @bot.message_handler(content_types=['text'])
    def group_message(message):
        if not common.STARTED:
            return
        if common.PARTICIPANTS and message.from_user.id == get_current_user_id():
            play_turn(message)

    bot.polling(none_stop=True)


if __name__ == '__main__':
    try:
        print("=== STARTING BOT ===")
        main()
    except:
        traceback.print_exc()
        os.execv(sys.executable, ['python'] + sys.argv)
