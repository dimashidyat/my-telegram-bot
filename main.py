import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Import handlers
from handlers.pempek import PempekHandler
from handlers.study import StudyHandler
from handlers.health import HealthHandler
from handlers.relationship import RelationshipHandler

# Setup basic logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
TOKEN = os.getenv("BOT_TOKEN", "7092522264:AAHsi2KM-8D8XcfIg09vptDyHiB28lRKQJY")

class DimasBot:
    def __init__(self):
        """Initialize bot and handlers"""
        try:
            # Initialize handlers
            self.pempek = PempekHandler()
            self.study = StudyHandler()
            self.health = HealthHandler()
            self.relationship = RelationshipHandler()
            
            # Track active menus
            self.active_menus = {}
            
            logger.info("Bot initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing bot: {e}")
            raise

    def get_main_menu_markup(self):
        """Create main menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("📝 Laporan Pempek", callback_data="menu_pempek"),
                InlineKeyboardButton("📚 BUMN Study", callback_data="menu_study")
            ],
            [
                InlineKeyboardButton("💪 Health Track", callback_data="menu_health"),
                InlineKeyboardButton("💑 Status Pacaran", callback_data="menu_relationship")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        try:
            user = update.effective_user
            text = (
                f"Hai {user.first_name}! 👋\n\n"
                "*Menu Utama:*\n"
                "1️⃣ *Pempek*\n"
                "• Input laporan harian\n"
                "• Track pemasukan/pengeluaran\n"
                "• Catat stok\n\n"
                "2️⃣ *BUMN Study*\n"
                "• Timer belajar\n"
                "• Track progress\n"
                "• Latihan soal\n\n"
                "3️⃣ *Health*\n"
                "• Workout tracker\n"
                "• Sleep monitor\n"
                "• Progress fisik\n\n"
                "4️⃣ *Relationship*\n"
                "• Love notes\n"
                "• Important dates\n"
                "• Quality time planner"
            )
            
            await update.message.reply_text(
                text,
                reply_markup=self.get_main_menu_markup(),
                parse_mode='Markdown'
            )
            logger.info(f"Start command from user {user.id}")
            
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await self.handle_error(update, context)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Route callbacks to appropriate handlers"""
        try:
            query = update.callback_query
            await query.answer()  # Acknowledge callback
            
            # Get user and callback data
            user_id = str(update.effective_user.id)
            data = query.data
            
            # Handle main menu navigation
            if data == "back_main":
                self.active_menus[user_id] = None
                await self.start(update, context)
                return
                
            # Route to appropriate handler
            if data.startswith("menu_"):
                menu_type = data.split("_")[1]
                self.active_menus[user_id] = menu_type
                
                if menu_type == "pempek":
                    await self.pempek.show_menu(update, context)
                elif menu_type == "study":
                    await self.study.show_menu(update, context)
                elif menu_type == "health":
                    await self.health.show_menu(update, context)
                elif menu_type == "relationship":
                    await self.relationship.show_menu(update, context)
                return
                
            # Handle submenu callbacks
            if user_id in self.active_menus:
                active_menu = self.active_menus[user_id]
                if active_menu == "pempek":
                    await self.pempek.handle_callback(update, context, data)
                elif active_menu == "study":
                    await self.study.handle_callback(update, context, data)
                elif active_menu == "health":
                    await self.health.handle_callback(update, context, data)
                elif active_menu == "relationship":
                    await self.relationship.handle_callback(update, context, data)
                    
        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            await self.handle_error(update, context)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        if update.message.text == "/start":
            await self.start(update, context)
        else:
            user_id = str(update.effective_user.id)
            if user_id in self.active_menus:
                active_menu = self.active_menus[user_id]
                if active_menu == "pempek":
                    await self.pempek.handle_message(update, context)
                elif active_menu == "study":
                    await self.study.handle_message(update, context)
                # Add other handlers as needed

    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors gracefully"""
        error_text = (
            "❌ Terjadi error.\n\n"
            "Coba:\n"
            "1. Ketik /start untuk mulai ulang\n"
            "2. Tunggu beberapa saat\n"
            "3. Pilih menu lagi"
        )
        
        try:
            if update.callback_query:
                await update.callback_query.message.reply_text(error_text)
            else:
                await update.message.reply_text(error_text)
        except Exception as e:
            logger.error(f"Error in error handler: {e}")

    def run(self):
        """Start the bot"""
        try:
            # Create application
            app = Application.builder().token(TOKEN).build()
            
            # Add handlers
            app.add_handler(CommandHandler("start", self.start))
            app.add_handler(CallbackQueryHandler(self.handle_callback))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            # Add error handler
            app.add_error_handler(self.handle_error)
            
            # Start polling
            logger.info("🤖 Bot starting...")
            app.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            logger.error(f"Critical error: {e}")
            raise

if __name__ == "__main__":
    try:
        bot = DimasBot()
        bot.run()
    except Exception as e:
        logger.critical(f"Bot failed to start: {e}")
