import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from pempek_handler import PempekHandler
import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
TOKEN = "7092522264:AAHsi2KM-8D8XcfIg09vptDyHiB28lRKQJY"

class DimasBot:
    def __init__(self):
        self.pempek_handler = PempekHandler()

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
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            "*🤖 SELAMAT DATANG DI DIMAS BOT!*\n\n"
            "Bot ini akan membantu:\n"
            "• 📝 Input laporan pempek\n"
            "• 📚 Track belajar BUMN\n"
            "• 💪 Monitor kebiasaan\n"
            "• ❤️ Manage relationship\n\n"
            "Pilih menu di bawah untuk mulai:"
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
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()

        if query.data == "menu_pempek":
            await self.pempek_handler.show_menu(update, context)
        elif query.data == "back_main":
            await self.start(update, context)
        # Add other menu handlers here

    def run(self):
        """Start the bot."""
        # Create application
        application = Application.builder().token(TOKEN).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Setup pempek handler
        self.pempek_handler.setup_handlers(application)

        # Start bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    bot = DimasBot()
    bot.run()
