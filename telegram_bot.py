import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define command handlers
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! I am your bot. How can I help you today?')

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('You can control me by sending these commands:\n\n'
                              '/start - Start the bot\n'
                              '/help - Get help')

def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)

def main() -> None:
    # Replace 'YOUR TOKEN HERE' with your actual bot token
    updater = Updater("YOUR TOKEN HERE")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()