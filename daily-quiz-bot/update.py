import json
import os
import requests


BOT_TOKEN = os.environ.get('BOT_TOKEN')
BASE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'


def process_updates():
    result = get_updates(None)
    updates = list()
    while result:
        updates.extend(result)
        offset = updates[-1]['update_id'] + 1
        result = get_updates(offset)
    return updates


def get_updates(offset):
    url = f'{BASE_URL}' + '/getUpdates'
    payload = {
        "allowed_updates": json.dumps(["poll_answer"])
    }
    if offset is not None:
        payload['offset'] = offset

    response = requests.get(url, data=payload)
    if response.status_code != 200:
        print("ERROR getting updates")
        print(response.text)
        return []
    else:
        return response.json()['result']
