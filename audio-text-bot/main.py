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
        prompt = random.choice(common.PROMPTS)
        bot.reply_to(message=message, text=prompt)
        # TODO This only accepts voice notes from the user who initiates
        # What should the logic be here? Perhaps, reply to message?
        common.CURRENT_USER_ID = message.from_user.id

    @bot.message_handler(content_types=['voice'])
    def receive_voice_note(message):
        if message.from_user.id != common.CURRENT_USER_ID:
            return
        file_id = message.voice.file_id
        file_path = bot.get_file(file_id).file_path
        audio_data = bot.download_file(file_path)
        filename = f'tmp/{str(random.random())[2:]}.mp3'
        print(filename)
        with open(filename, "wb") as binary_file:
            binary_file.write(audio_data)
        transcribed_text = utils.transcribe(filename)
        if transcribed_text is None:
            bot.send_message(chat_id=message.chat.id, text="Sorry something went wrong!")
        else:
            duration_text = utils.duration_lib(transcribed_text)
            text = f'You said: {transcribed_text}\n{duration_text}'
            bot.send_message(chat_id=message.chat.id, text=text)
        common.CURRENT_USER_ID = None
        os.remove(filename)

    bot.polling(non_stop=True, skip_pending=True)


if __name__ == '__main__':
    main()
