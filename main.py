import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Basic commands
def start(update, context):
    update.message.reply_text(
        text='Halo! Bot udah aktif nih. Ketik /help buat liat commands yang tersedia.',
        parse_mode=ParseMode.MARKDOWN
    )

def help(update, context):
    help_text = """
*Commands yang tersedia:*
/start - Mulai bot
/help - Liat commands yang ada
/status - Cek status bot
    """
    update.message.reply_text(
        text=help_text,
        parse_mode=ParseMode.MARKDOWN
    )

def status(update, context):
    update.message.reply_text('Bot lagi aktif dan siap dipakai! 🟢')

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    try:
        # Get environment variables
        TOKEN = os.getenv('BOT_TOKEN')
        if not TOKEN:
            raise ValueError("No TOKEN provided!")

        # Create updater
        updater = Updater(TOKEN, use_context=True)
        dp = updater.dispatcher

        # Add handlers
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", help))
        dp.add_handler(CommandHandler("status", status))
        
        # Log errors
        dp.add_error_handler(error)

        # Start bot
        updater.start_polling()
        logger.info("Bot started successfully!")
        
        # Run until Ctrl+C
        updater.idle()
        
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")

if __name__ == '__main__':
    main()
