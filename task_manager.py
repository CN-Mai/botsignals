import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import aioschedule
from signal_generator import AdvancedSignalGenerator
from database import User, Alert, Position

class TaskManager:
    def __init__(self, bot, config, db_session):
        self.bot = bot
        self.config = config
        self.db_session = db_session
        self.signal_generator = AdvancedSignalGenerator(config)
        self.logger = logging.getLogger(__name__)
    
    async def start_background_tasks(self):
        """Start all background tasks"""
        aioschedule.every(1).minutes.do(self.check_alerts)
        aioschedule.every(5).minutes.do(self.update_signals)
        aioschedule.every(1).hours.do(self.check_subscriptions)
        aioschedule.every(4).hours.do(self.update_models)
        
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(1)
    
    async def check_alerts(