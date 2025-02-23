from telegram import Bot, Update, Message
from telegram.ext import Updater
import asyncio
from datetime import datetime
from config import BotConfig
from main import CryptoSignalBot

class TestSession:
    def __init__(self):
        self.config = BotConfig()
        self.bot = CryptoSignalBot()
        self.user_id = 123456789  # Test user ID
        self.username = "CN-Mai"
        self.timestamp = "2025-02-23 19:12:13"

    async def simulate_command(self, command: str):
        print(f"\n📝 Testing command: {command}")
        print(f"⏰ Timestamp: {self.timestamp}")
        print(f"👤 User: {self.username}")
        print("-------------------------")
        
        try:
            # Simulate message
            message = Message(
                message_id=1,
                date=datetime.utcnow(),
                chat_id=self.user_id,
                text=command,
                from_user={'id': self.user_id, 'username': self.username}
            )
            
            # Process command
            if command == "/start":
                await self.bot.start_command(message)
            elif command == "/signals":
                await self.bot.signals_command(message)
            elif command == "/subscribe":
                await self.bot.subscribe_command(message)
            elif command == "/portfolio":
                await self.bot.portfolio_command(message)
            elif command.startswith("/alert"):
                await self.bot.set_alert_command(message)
                
            print("✅ Command processed successfully")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")

async def run_tests():
    test = TestSession()
    
    # Test basic commands
    await test.simulate_command("/start")
    await asyncio.sleep(1)
    
    await test.simulate_command("/signals")
    await asyncio.sleep(1)
    
    await test.simulate_command("/subscribe")
    await asyncio.sleep(1)
    
    await test.simulate_command("/portfolio")
    await asyncio.sleep(1)
    
    # Test alert command
    await test.simulate_command("/alert BTC 50000")
    await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_tests())