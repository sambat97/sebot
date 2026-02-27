import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
SERVER_ID = os.getenv("SERVER_ID", "co").lower().strip()
