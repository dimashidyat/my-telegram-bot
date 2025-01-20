import logging
import traceback
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    PicklePersistence,
    ContextTypes,
    filters,
)
from config import TOKEN
from handlers.pempek import PempekHandler
from handlers.study import StudyHandler
from handlers.schedule import ScheduleHandler
from handlers.health import HealthHandler
from handlers.relationship import RelationshipHandler

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename=f'bot_logs_{datetime.now().strftime("%Y%m%d")}.log',
)
logger = logging.getLogger(__name__)

class DimasBot:
    def __init__(self):
        """Initialize bot and handlers"""
        try:
            self.pempek = PempekHandler()
            self.study = StudyHandler()
            self.schedule = ScheduleHandler()
            self.health = HealthHandler()
            self.relationship = RelationshipHandler()
            self.active_menus = {}  # Track active menus per user
        except Exception as e:
            logger.error(f"Error initializing bot: {e}")
            raise

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler with error handling"""
        try:
            user_id = update.effective_user.id
            self.active_menus[user_id] = "main"

            keyboard = [
                [
                    InlineKeyboardButton("📝 Laporan Pempek", callback_data="pempek"),
                    InlineKeyboardButton("📚 Study BULOG", callback_data="study"),
                ],
                [
                    InlineKeyboardButton("⏰ Jadwal", callback_data="schedule"),
                    InlineKeyboardButton("💪 Health", callback_data="health"),
                ],
                [InlineKeyboardButton("💕 Status Pacaran", callback_data="relationship")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "Halo bro! Bot aktif nich ✨\n\n"
                "Pilih menu yang lo butuhin:",
                reply_markup=reply_markup,
            )

            # Save user data
            if "users" not in context.bot_data:
                context.bot_data["users"] = {}
            context.bot_data["users"][user_id] = {
                "last_active": datetime.now(),
                "name": update.effective_user.full_name,
            }

        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await self.handle_error(update, context)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks with error recovery"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id

            # Validate callback
            if not query or not query.data:
                raise ValueError("Invalid callback data")

            await query.answer()  # Acknowledge callback

            # Handle menu navigation
            if query.data == "back_main":
                await self.start(update, context)
                return

            # Route to appropriate handler
            handlers = {
                "pempek": self.pempek.show_menu,
                "study": self.study.show_menu,
                "schedule": self.schedule.show_menu,
                "health": self.health.show_menu,
                "relationship": self.relationship.show_menu,
            }

            if query.data in handlers:
                self.active_menus[user_id] = query.data
                await handlers[query.data](update, context)
            else:
                # Handle sub-menu callbacks
                current_menu = self.active_menus.get(user_id)
                if current_menu == "pempek":
                    await self.pempek.handle_callback(query.data, update, context)
                elif current_menu == "study":
                    await self.study.handle_callback(query.data, update, context)
                # Add other sub-menus as needed

        except Exception as e:
            logger.error(f"Error handling callback: {e}\n{traceback.format_exc()}")
            await self.handle_error(update, context)

    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Central error handler"""
        try:
            error_message = (
                "Waduh, error nih 😅\nCoba:\n1. Ketik /start\n2. Tunggu bentar\n3. Pilih menu lagi"
            )

            if update.callback_query:
                await update.callback_query.message.reply_text(error_message)
            elif update.message:
                await update.message.reply_text(error_message)

        except Exception as e:
            logger.error(f"Error in error handler: {e}")

    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unknown commands"""
        await update.message.reply_text(
            "Command ga valid nih 🤔\nKetik /start aja ya!"
        )

    def run(self):
        """Run bot with persistence and error handling"""
        try:
            # Setup persistence
            persistence = PicklePersistence(filepath="bot_data")

            # Create application
            app = Application.builder() \
                .token(TOKEN) \
                .persistence(persistence) \
                .build()

            # Add handlers
            app.add_handler(CommandHandler("start", self.start))
            app.add_handler(CallbackQueryHandler(self.handle_callback))
            app.add_error_handler(self.handle_error)

            # Add fallback for unknown commands
            app.add_handler(MessageHandler(
                filters.COMMAND & (~filters.Regex("^/start$")),
                self.unknown_command
            ))

            # Start polling
            print("🚀 Bot started successfully!")
            app.run_polling(allowed_updates=Update.ALL_TYPES)

        except Exception as e:
            logger.error(f"Critical error running bot: {e}\n{traceback.format_exc()}")
            raise


if __name__ == "__main__":
    bot = DimasBot()
    bot.run()
