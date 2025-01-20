import logging
import json
import os
from datetime import datetime, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Configuration
TOKEN = "7092522264:AAHsi2KM-8D8XcfIg09vptDyHiB28lRKQJY"

class DimasBot:
    def __init__(self):
        # Initialize storage
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data containers
        self.pempek_data = self.load_data("pempek")
        self.study_data = self.load_data("study")
        self.health_data = self.load_data("health")
        
        # Track active menu per user
        self.active_menu = {}
        
        # Initialize handlers
        self.menu_handlers = {
            'pempek': self.handle_pempek_menu,
            'study': self.handle_study_menu,
            'health': self.handle_health_menu,
            'relationship': self.handle_relationship_menu
        }

    def load_data(self, data_type: str) -> dict:
        """Load data from file with error handling"""
        try:
            file_path = os.path.join(self.data_dir, f"{data_type}_data.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {data_type} data: {e}")
        return {}

    def save_data(self, data_type: str, data: dict):
        """Save data to file with backup"""
        try:
            # Save main file
            file_path = os.path.join(self.data_dir, f"{data_type}_data.json")
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Save backup with timestamp
            backup_path = os.path.join(self.data_dir, f"{data_type}_backup_{datetime.now().strftime('%Y%m%d')}.json")
            with open(backup_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving {data_type} data: {e}")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send main menu"""
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
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = (
            "*🤖 HALO DIMAS!*\n\n"
            "Pilih menu:\n\n"
            "1️⃣ *Pempek*\n"
            "• Input laporan harian\n"
            "• Track pemasukan/pengeluaran\n"
            "• Catat stok\n\n"
            "2️⃣ *BUMN Study*\n"
            "• Timer belajar\n"
            "• Latihan soal\n"
            "• Progress tracking\n\n"
            "3️⃣ *Health*\n"
            "• Workout reminder\n"
            "• Sleep tracker\n"
            "• Progress fisik\n\n"
            "4️⃣ *Relationship*\n"
            "• Love notes\n"
            "• Important dates\n"
            "• Quality time planner"
        )

        if update.callback_query:
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
        """Route callbacks to appropriate handlers"""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            user_id = str(update.effective_user.id)

            # Handle menu navigation
            if data == "back_main":
                await self.start(update, context)
                return
                
            if data.startswith("menu_"):
                menu_type = data.split("_")[1]
                self.active_menu[user_id] = menu_type
                await self.menu_handlers[menu_type](update, context)
                return

            # Handle specific menu callbacks
            if user_id in self.active_menu:
                active_menu = self.active_menu[user_id]
                if active_menu == "pempek":
                    await self.handle_pempek_callback(update, context, data)
                elif active_menu == "study":
                    await self.handle_study_callback(update, context, data)
                elif active_menu == "health":
                    await self.handle_health_callback(update, context, data)
                elif active_menu == "relationship":
                    await self.handle_relationship_callback(update, context, data)

        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            await self.handle_error(update, context)

    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Global error handler"""
        error_text = (
            "😅 Waduh error nih...\n\n"
            "Coba:\n"
            "1. Ketik /start\n"
            "2. Tunggu bentar\n"
            "3. Pilih menu lagi\n\n"
            "Kalo masih error, chat developernya ya!"
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
            
            # Add handler for messages
            app.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handle_message
            ))
            
            # Add handler for unknown commands
            app.add_handler(MessageHandler(
                filters.COMMAND & ~filters.Regex("^/start$"),
                lambda u, c: u.message.reply_text("Command ga valid! Ketik /start aja.")
            ))

            # Start bot
            print("🤖 Bot started!")
            app.run_polling(allowed_updates=Update.ALL_TYPES)

        except Exception as e:
            logger.error(f"Critical error: {e}")
            raise

if __name__ == "__main__":
    bot = DimasBot()
    bot.run()
