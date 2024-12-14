from dotenv import load_dotenv
from os import getenv

load_dotenv()

# Credential
BOT_TOKEN = getenv('BOT_TOKEN')
# Admin
ADMIN_CHAT_ID = getenv('ADMIN_CHAT_ID')
# Redis_settings
REDIS_HOST = getenv('REDIS_HOST', 'redis_app')
REDIS_PORT = int(getenv('REDIS_PORT', 6379))
