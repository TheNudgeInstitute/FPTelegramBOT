import os

import openai
import whisper
import requests

from typing import Optional

STT_MODEL = os.environ.get('MODEL_NAME', 'tiny.en')
DURATION_PROMPT = os.environ.get('DURATION_PROMPT', 'What is the speaking duration of this audio: ')
DURATION_MODEL = os.environ.get('DURATION_MODEL', 'text-davinci-001')
OPEN_API_KEY = os.environ.get('OPEN_API_KEY')
openai.api_key = os.environ.get('OPEN_API_KEY')


def transcribe(filename: str) -> Optional[str]:
    try:
        model = whisper.load_model(STT_MODEL)
        result = model.transcribe(filename)
        return result['text'].strip()
    except Exception as e:
        print(e)
        return None


def duration_lib(text: str) -> str:
    try:
        response = openai.Completion.create(
            model=DURATION_MODEL,
            prompt=(f'{DURATION_PROMPT} {text}'),
            temperature=0,
            max_tokens=60,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        corrected_text = response['choices'][0]['text']
        return corrected_text.strip()
    except Exception as e:
        print(e)
        return ''


def duration_http(text: str) -> str:
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPEN_API_KEY}',
        }
        json_data = {
            'model': DURATION_MODEL,
            'prompt': f'{DURATION_PROMPT} {text}',
            'temperature': 0,
            'max_tokens': 60,
            'top_p': 1,
            'frequency_penalty': 0,
            'presence_penalty': 0,
        }
        response = requests.post('https://api.openai.com/v1/completions', headers=headers, json=json_data)
        if response.status_code != 200:
            raise Exception(response.text)
        corrected_text = response.json()['choices'][0]['text']
        return corrected_text.strip()
    except Exception as e:
        print(e)
        return ''
