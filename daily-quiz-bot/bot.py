import json
import os

import requests

BOT_TOKEN = os.environ.get('BOT_TOKEN')
BASE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'


def send_poll(prompt, options, correct_index, explanation):
    parameters = {
        'chat_id': os.environ.get('GROUP_ID'),
        'question': prompt,
        'options': json.dumps(options),
        'is_anonymous': False,
        'type': 'quiz',
        'correct_option_id': correct_index,
        'explanation': explanation
    }
    response = requests.get(BASE_URL + '/sendPoll', data=parameters)
    if response.status_code != 200:
        print(response.text)
        return None
    response_json = response.json()
    return response_json.get('result')


def stop_poll(message_id):
    parameters = {
        'chat_id': os.environ.get('GROUP_ID'),
        'message_id': message_id
    }
    response = requests.get(BASE_URL + '/stopPoll', data=parameters)
    if response.status_code != 200:
        print(response.text)
        return None
    response_json = response.json()
    return response_json.get('result')


def send_message(message_text):
    parameters = {
        'chat_id': os.environ.get('GROUP_ID'),
        'text': message_text
    }
    response = requests.get(BASE_URL + '/sendMessage', data=parameters)
    if response.status_code != 200:
        print(response.text)
        return None
    response_json = response.json()
    return response_json.get('result')
