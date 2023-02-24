import openai
import os

from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPEN_API_KEY')


def grammar_check(message_text):
    # Generate completions for the text
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=(f"Correct the grammar in this sentence and provide an explanation suitable to a1 level student:\n{message_text}"),
        temperature=0,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    print(response)
    result = response["choices"][0]["text"].strip().split('\n\n')
    return result[0].strip(), '\n'.join(result[1:])
