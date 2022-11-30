import os
import json
import requests

GROUP_ID = os.environ.get('GROUP_ID')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
BASE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'


def send_poll(prompt, options, correct_index, explanation):
    parameters = {
        "chat_id": GROUP_ID,
        "question": prompt,
        "options": json.dumps(options),
        "is_anonymous": False,
        "type": "quiz",
        "correct_option_id": correct_index,
        "explanation": explanation
    }
    response = requests.get(BASE_URL+'/sendPoll', data=parameters)
    response_json = response.json()
    return response_json['result']['poll']['id']
