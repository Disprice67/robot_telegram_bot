from dotenv import load_dotenv
from os import getenv

load_dotenv()

# Credential
BOT_TOKEN = getenv('BOT_TOKEN')
# Admin
ADMIN_CHAT_ID = getenv('ADMIN_CHAT_ID')
# Redis_settings
REDIS_URL = getenv('REDIS_URL')
