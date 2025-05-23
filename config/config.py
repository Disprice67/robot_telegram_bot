from dotenv import load_dotenv
from os import getenv
from pathlib import Path

load_dotenv()

# Root_dir
ROOT_DIR = Path(__file__).parent.parent.parent
# Robot_files
ROBOT_FILES = ROOT_DIR / 'data' / 'robot'
# Credential
BOT_TOKEN = getenv('BOT_TOKEN')
# Admin
ADMIN_CHAT_ID = getenv('ADMIN_CHAT_ID')
# Redis_settings
REDIS_HOST = 'redis://' + getenv('REDIS_HOST', 'redis_app')
REDIS_PORT = int(getenv('REDIS_PORT', 6379))
