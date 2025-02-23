import asyncio
from datetime import datetime
from telegram import Bot
from config import BotConfig

async def test_bot_functionality():
    config = BotConfig()
    bot = Bot(token=config.TELEGRAM_TOKEN)
    
    print(f"🔄 Starting bot tests at {datetime.utcnow()}")
    print(f"👤 Test User: {config.CURRENT_USER}")
    
    try:
        # 1. Test bot connection
        bot_info = await bot.get_me()
        print(f"\n✅ Bot Connection Success!")
        print(f"Bot Username: @{bot_info.username}")
        print(f"Bot Name: {bot_info.first_name}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Bot Connection Failed: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_bot_functionality())