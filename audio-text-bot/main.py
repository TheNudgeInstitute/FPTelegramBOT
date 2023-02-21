import os
import random

import telebot
from dotenv import load_dotenv
load_dotenv()

import common
import utils

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))


def main():
    @bot.message_handler(commands=['talk'])
    def send_audio_prompt(message):
        if common.CURRENT_USER_ID is not None:
            return
        print("Received command from user:", message.from_user.id)
        prompt = random.choice(common.PROMPTS)
        common.CURRENT_PROMPT = prompt
        print("Prompt:", prompt)
        bot.reply_to(message=message, text=prompt)
        # TODO This only accepts voice notes from the user who initiates
        # What should the logic be here? Perhaps, reply to message?
        common.CURRENT_USER_ID = message.from_user.id

    @bot.message_handler(content_types=['voice'])
    def receive_voice_note(message):
        if message.from_user.id != common.CURRENT_USER_ID:
            return
        print("Received audio from user:", message.from_user.id)
        file_id = message.voice.file_id
        file_path = bot.get_file(file_id).file_path
        audio_data = bot.download_file(file_path)
        filename = f'tmp/{str(random.random())[2:]}.mp3'
        print("Persisted file:", filename)
        with open(filename, "wb") as binary_file:
            binary_file.write(audio_data)
        transcribed_text = utils.transcribe(filename)
        print("Transcribed text:", transcribed_text)
        if transcribed_text is None:
            bot.send_message(chat_id=message.chat.id, text="Sorry something went wrong!")
        else:
            # corrected_text = utils.grammar_check(transcribed_text)
            # TODO Check this
            corrected_text = common.CURRENT_PROMPT
            print("Corrected text:", corrected_text)
            if corrected_text is None:
                bot.send_message(chat_id=message.chat.id, text=transcribed_text)
            else:
                is_correct = transcribed_text.casefold() == corrected_text.casefold()
                text = f'{transcribed_text} {"✅" if is_correct else "❗"}'
                bot.send_message(chat_id=message.chat.id, text=text)
                print("Result:", text)
        print("-" * 20)
        common.CURRENT_USER_ID = None
        common.CURRENT_PROMPT = None
        os.remove(filename)

    print("=== STARTING AUDIO-TEXT-BOT === ")
    bot.polling(non_stop=True, skip_pending=True)


if __name__ == '__main__':
    main()
