import time

import common
from main import skip_turn, start_game
from message import send_join_prompt
from utils import get_current_user_id


def start_join_timer(chat_id):
    for i in range(60, -1, -1):
        if not common.JOIN_MODE:
            break
        if i == 60:
            send_join_prompt(chat_id, i)
        elif i == 40:
            send_join_prompt(chat_id, i)
        elif i == 20:
            send_join_prompt(chat_id, i)
        elif i == 0:
            if not common.STARTED:
                common.STARTED = True
                start_game(chat_id)
        time.sleep(1)


def answer_timer(user_id, round, chat_id, turn_time):
    for i in range(turn_time, -1, -1):
        if i == 0 and common.IS_ACTIVE and user_id == get_current_user_id() and round == common.ROUND:
            skip_turn(chat_id)
        time.sleep(1)

# TODO Game timer of 3 minutes 30 seconds.
