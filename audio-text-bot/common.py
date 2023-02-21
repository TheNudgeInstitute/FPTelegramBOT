from db import Database

# Database Connection #
DB = Database()
PROMPTS = DB.get_prompts()

# Turn Variables
CURRENT_USER_ID = None
CURRENT_PROMPT = None
