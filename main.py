import os
import sys
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from utils.logger import logger, log_start, log_error
from handlers.pempek import PempekHandler
from handlers.study import StudyHandler
from handlers.health import HealthHandler
from handlers.relationship import RelationshipHandler

# Bot token dari environment variable atau config
TOKEN = os.getenv("BOT_TOKEN") or "7092522264:AAHsi2KM-8D8XcfIg09vptDyHiB28lRKQJY"

class DimasBot:
    def __init__(self):
        # Log startup info
        log_start()
        
        try:
            # Initialize handlers
            logger.info("Initializing handlers...")
            self.pempek_handler = PempekHandler()
            self.study_handler = StudyHandler()
            self.health_handler = HealthHandler()
            self.relationship_handler = RelationshipHandler()
            
            # Track active menus
            self.active_menu = {}
            
            logger.info("Handlers initialized successfully")
            
        except Exception as e:
            log_error(e)
            raise

    async def start(self, update: Update, context):
        """Handle /start command"""
        try:
            logger.info(f"Start command received from user {update.effective_user.id}")
            # Your existing start menu code here
            await update.message.reply_text(
                "Bot started! Choose a menu:",
                reply_markup=self.get_main_menu_markup()
            )
        except Exception as e:
            log_error(e)
            await self.handle_error(update, context)

    def run(self):
        """Start the bot"""
        try:
            logger.info("Starting bot...")
            
            # Print debugging info
            logger.info(f"Python version: {sys.version}")
            logger.info(f"Current working directory: {os.getcwd()}")
            logger.info(f"TOKEN length: {len(TOKEN)}")
            
            # Create application
            app = Application.builder().token(TOKEN).build()
            
            # Add handlers
            logger.info("Adding handlers...")
            app.add_handler(CommandHandler("start", self.start))
            app.add_handler(CallbackQueryHandler(self.handle_callback))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            # Add error handler
            app.add_error_handler(self.error_handler)
            
            # Start polling
            logger.info("Starting polling...")
            app.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            log_error(e)
            logger.error("Bot failed to start!")
            raise

    async def error_handler(self, update: Update, context):
        """Handle errors globally"""
        log_error(context.error)
        try:
            await update.message.reply_text(
                "Terjadi error. Bot akan restart otomatis.\n"
                "Silakan coba lagi dalam beberapa saat."
            )
        except:
            pass

if __name__ == "__main__":
    logger.info("Script started")
    try:
        bot = DimasBot()
        logger.info("Bot instance created")
        bot.run()
    except Exception as e:
        log_error(e)
        sys.exit(1)
