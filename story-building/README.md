# Story Building Bot


### Required Environment Variables

```properties
BOT_TOKEN=

OPEN_API_KEY=

AWS_SERVICE_NAME=
AWS_REGION_NAME=
AWS_ACCESS_KEY=
AWS_SECRET_ACCESS_KEY=
```

### Preparing the Bot
```shell
cd story-building
python3 -m venv venv/
source venv/bin/activate
pip3 install -r requirements.txt 
python3 main.py
```

### Running the Bot
```shell
# Run in background
nohup python3 main.py

# Stop the bot
pgrep -f -l main.py
kill PID 
```
