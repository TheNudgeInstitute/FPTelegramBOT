### Dependencies
* https://pypi.org/project/openai-whisper/
* ffmpeg
* https://github.com/eternnoir/pyTelegramBotAPI
* https://platform.openai.com/docs/api-reference/completions/create


### Create temp folder
```shell
mkdir tmp
```

### .env file
```
# Bot token, with Privacy mode disabled. 
BOT_TOKEN=
OPEN_API_KEY=

STT_MODEL=tiny.en
DURATION_PROMPT=What is the speaking duration of this audio:
DURATION_MODEL=text-davinci-001
```

### Requirements
* ffmpeg
```
sudo apt update && sudo apt install ffmpeg
```
