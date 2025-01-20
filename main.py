import logging
import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from handlers.pempek import PempekHandler
from handlers.study import StudyHandler
from handlers.health import HealthHandler
from handlers.relationship import RelationshipHandler
from handlers.schedule import ScheduleHandler
from config import TOKEN

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class DimasBot:
    def __init__(self):
        """Initialize bot and handlers"""
        self.pempek_handler = PempekHandler()
        self.study_handler = StudyHandler()
        self.health_handler = HealthHandler()
        self.relationship_handler = RelationshipHandler()
        self.schedule_handler = ScheduleHandler()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send main menu when /start command is issued."""
        keyboard = [
            [
                InlineKeyboardButton("📝 Laporan Pempek", callback_data="menu_pempek"),
                InlineKeyboardButton("📚 BUMN Study", callback_data="menu_study")
            ],
            [
                InlineKeyboardButton("💪 Daily Track", callback_data="menu_track"),
                InlineKeyboardButton("❤️ Relationship", callback_data="menu_relationship")
            ],
            [
                InlineKeyboardButton("📅 Schedule", callback_data="menu_schedule")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            "*🤖 SELAMAT DATANG DI DIMAS BOT!*\n\n"
            "Bot ini akan membantu:\n"
            "• 📝 Input laporan pempek\n"
            "• 📚 Track belajar BUMN\n"
            "• 💪 Monitor kebiasaan\n"
            "• ❤️ Manage relationship\n"
            "• 📅 Atur jadwal harian\n\n"
            "Pilih menu di bawah untuk mulai:"
        )

        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all button callbacks"""
        query = update.callback_query
        await query.answer()

        # Route callbacks to appropriate handlers
        if query.data == "menu_pempek" or query.data.startswith("pempek_"):
            await self.pempek_handler.handle_callback(update, context)
        elif query.data == "menu_study" or query.data.startswith("study_"):
            await self.study_handler.handle_callback(update, context)
        elif query.data == "menu_track" or query.data.startswith("track_"):
            await self.health_handler.handle_callback(update, context)
        elif query.data == "menu_relationship" or query.data.startswith("relationship_"):
            await self.relationship_handler.handle_callback(update, context)
        elif query.data == "menu_schedule" or query.data.startswith("schedule_"):
            await self.schedule_handler.handle_callback(update, context)
        elif query.data == "back_main":
            await self.start(update, context)

    def setup_handlers(self, application: Application):
        """Setup all command and callback handlers"""
        # Basic handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Setup module handlers
        self.pempek_handler.setup_handlers(application)
        self.study_handler.setup_handlers(application)
        self.health_handler.setup_handlers(application)
        self.relationship_handler.setup_handlers(application)
        self.schedule_handler.setup_handlers(application)

    def run(self):
        """Start the bot"""
        try:
            # Create application
            application = Application.builder().token(TOKEN).build()
            
            # Setup handlers
            self.setup_handlers(application)
            
            # Start bot
            logger.info("Starting bot...")
            application.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            sys.exit(1)

if __name__ == '__main__':
    bot = DimasBot()
    bot.run()
