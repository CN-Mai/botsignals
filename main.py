import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext
from config import BotConfig
from dynamic_stats_manager import EnhancedStatsManager
from language_manager import LanguageManager
from user_preferences import UserPreferencesManager
from news_manager import NewsManager

class CryptoSignalBot:
    def __init__(self):
        self.config = BotConfig()
        self.stats_manager = EnhancedStatsManager()
        self.language_manager = LanguageManager()
        self.user_prefs_manager = UserPreferencesManager()
        self.news_manager = NewsManager(self.config.NEWS_API_KEY)
        
        # Create Telegram bot application
        self.application = Application.builder().token(self.config.TELEGRAM_TOKEN).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("dashboard", self.dashboard_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        self.application.add_handler(CommandHandler("language", self.language_command))
        self.application.add_handler(CommandHandler("news", self.news_command))
        
    async def start_command(self, update: Update, context: CallbackContext):
        """Handle /start command"""
        welcome_message = f"""
🚀 Welcome to Ultimate Crypto Signals Bot! 
Current Users Online: {random.randint(1500, 2500)} 🟢
"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Market Analysis", callback_data='market_analysis'),
                InlineKeyboardButton("💎 Go Premium", callback_data='premium_info')
            ],
            [
                InlineKeyboardButton("⚡ Quick Signals", callback_data='quick_signals'),
                InlineKeyboardButton("📈 Top Gainers", callback_data='top_gainers')
            ],
            [
                InlineKeyboardButton("💰 Portfolio", callback_data='portfolio'),
                InlineKeyboardButton("⭐ My Account", callback_data='account')
            ],
            [
                InlineKeyboardButton("📰 Latest News", callback_data='latest_news')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    
    async def dashboard_command(self, update: Update, context: CallbackContext):
        """Show live dashboard"""
        user_id = update.effective_user.id
        prefs = await self.user_prefs_manager.get_user_preferences(user_id)
        dashboard = await self.stats_manager.generate_enhanced_dashboard(prefs)
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Refresh Stats", callback_data='refresh_stats'),
                InlineKeyboardButton("📊 Detailed Analytics", callback_data='detailed_stats')
            ],
            [
                InlineKeyboardButton("👥 Community", callback_data='community'),
                InlineKeyboardButton("🏆 Leaderboard", callback_data='leaderboard')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(dashboard, reply_markup=reply_markup)
    
    async def settings_command(self, update: Update, context: CallbackContext):
        """Handle settings command"""
        user_id = update.effective_user.id
        prefs = await self.user_prefs_manager.get_user_preferences(user_id)
        
        settings_message = f"""
⚙️ Your Settings:

🗣️ Language: {self.language_manager.supported_languages[prefs.language].flag} {self.language_manager.supported_languages[prefs.language].native_name}
🌍 Timezone: {prefs.timezone}
💰 Currency: {prefs.currency}
🎨 Theme: {prefs.theme.capitalize()}
🔔 Notifications: {prefs.notification_level.capitalize()}
📊 Default Chart: {prefs.chart_type.capitalize()}
⏱️ Default Timeframe: {prefs.timeframe_default}
⚠️ Risk Level: {prefs.risk_level.capitalize()}
"""

        keyboard = [
            [
                InlineKeyboardButton("🗣️ Language", callback_data='settings_language'),
                InlineKeyboardButton("🌍 Timezone", callback_data='settings_timezone')
            ],
            [
                InlineKeyboardButton("💰 Currency", callback_data='settings_currency'),
                InlineKeyboardButton("🎨 Theme", callback_data='settings_theme')
            ],
            [
                InlineKeyboardButton("🔔 Notifications", callback_data='settings_notifications'),
                InlineKeyboardButton("📊 Chart Type", callback_data='settings_chart')
            ],
            [
                InlineKeyboardButton("⏱️ Timeframe", callback_data='settings_timeframe'),
                InlineKeyboardButton("⚠️ Risk Level", callback_data='settings_risk')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(settings_message, reply_markup=reply_markup)
    
    async def language_command(self, update: Update, context: CallbackContext):
        """Change language"""
        user_id = update.effective_user.id
        new_language = context.args[0] if context.args else 'en'
        success = await self.user_prefs_manager.update_preference(user_id, 'language', new_language)
        
        if success:
            await update.message.reply_text(f"Language updated to {new_language}")
        else:
            await update.message.reply_text("Failed to update language")
    
    async def news_command(self, update: Update, context: CallbackContext):
        """Fetch and display the latest news"""
        news = await self.news_manager.get_latest_news()
        news_message = "📰 *Latest Cryptocurrency News*:\n\n" + "\n\n".join(
            [f"[{article['title']}]({article['url']})\n_{article['description']}_"
             for article in news[:5]]
        )
        await update.message.reply_text(news_message, parse_mode='Markdown')
    
    async def run(self):
        """Start the bot"""
        await self.application.start()
        await self.application.idle()

if __name__ == "__main__":
    bot = CryptoSignalBot()
    asyncio.run(bot.run())