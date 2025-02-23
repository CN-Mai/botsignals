import os
from dotenv import load_dotenv

load_dotenv()

class BotConfig:
    def __init__(self):
        self.TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.REDIS_URL = os.getenv("REDIS_URL")
        self.BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
        self.BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
        self.NEWS_API_KEY = os.getenv("NEWS_API_KEY")
        self.ENABLE_PREMIUM_FEATURES = os.getenv("ENABLE_PREMIUM_FEATURES", "false").lower() == "true"
        self.ENABLE_DEBUG_MODE = os.getenv("ENABLE_DEBUG_MODE", "false").lower() == "true"