from dotenv import load_dotenv

from db import Database

load_dotenv()

# Database Connection #
DB = Database()

# Game Mode #
IS_ACTIVE = bool()
JOIN_MODE = bool()
STARTED = bool()

# Participant Data #
PARTICIPANT_MAP = dict()  # user_id -> first_name
PARTICIPANTS = list()  # user_id

# Game Data #
CURRENT_PARTICIPANT_INDEX = None
ROUND = int()
STORY = list()

# Game Variables #
PROMPTS = DB.get_prompts()
MIN_PARTICIPANTS = 2
MAX_PARTICIPANTS = 3
MAX_ROUNDS = 3
TURN_TIME_LIMIT = 45
