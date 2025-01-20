import logging
import traceback
from datetime import datetime
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

# Bot token
TOKEN = "7092522264:AAHsi2KM-8D8XcfIg09vptDyHiB28lRKQJY"

class DimasBot:
    def __init__(self):
        self.menu_handlers = {}
        self.active_menus = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send main menu when /start command is issued"""
        try:
            keyboard = [
                [
                    InlineKeyboardButton("📝 Laporan Pempek", callback_data="menu_pempek"),
                    InlineKeyboardButton("📚 BUMN Study", callback_data="menu_study")
                ],
                [
                    InlineKeyboardButton("⏰ Jadwal", callback_data="menu_schedule"),
                    InlineKeyboardButton("💪 Health", callback_data="menu_health")
                ],
                [InlineKeyboardButton("💕 Status Pacaran", callback_data="menu_relationship")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            text = (
                "*🤖 SELAMAT DATANG DI DIMAS BOT!*\n\n"
                "Bot ini akan membantu:\n"
                "• 📝 Input laporan pempek\n"
                "• 📚 Track belajar BUMN\n"
                "• ⏰ Atur jadwal harian\n"
                "• 💪 Monitor kesehatan\n"
                "• 💕 Manage relationship\n\n"
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

        except Exception as e:
            logger.error(f"Error in start command: {traceback.format_exc()}")
            await self.handle_error(update, context)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id

            # Always answer callback query
            await query.answer()

            # Check if returning to main menu
            if query.data == "back_main":
                await self.start(update, context)
                return

            # Handle menu selection
            if query.data.startswith("menu_"):
                menu_type = query.data.split("_")[1]
                self.active_menus[user_id] = menu_type
                
                # Show appropriate menu
                if menu_type == "pempek":
                    await self.show_pempek_menu(update, context)
                elif menu_type == "study":
                    await self.show_study_menu(update, context)
                # Add other menus here
                return

            # Handle sub-menu actions
            current_menu = self.active_menus.get(user_id)
            if current_menu == "pempek":
                await self.handle_pempek_callback(query.data, update, context)
            elif current_menu == "study":
                await self.handle_study_callback(query.data, update, context)
            # Add other sub-menu handlers

        except Exception as e:
            logger.error(f"Error handling callback: {traceback.format_exc()}")
            await self.handle_error(update, context)

    async def show_pempek_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show pempek reporting menu"""
        keyboard = [
            [
                InlineKeyboardButton("💰 Input Modal", callback_data="pempek_modal"),
                InlineKeyboardButton("📦 Sisa Stock", callback_data="pempek_stock")
            ],
            [
                InlineKeyboardButton("💵 Input Setoran", callback_data="pempek_setoran"),
                InlineKeyboardButton("📊 Laporan", callback_data="pempek_report")
            ],
            [InlineKeyboardButton("🔙 Menu Utama", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            "*📝 MENU LAPORAN PEMPEK*\n\n"
            f"Tanggal: {datetime.now().strftime('%d/%m/%Y')}\n\n"
            "Pilih menu:\n"
            "• Modal = Input pengeluaran\n"
            "• Stock = Sisa dagangan\n"
            "• Setoran = Total pendapatan\n"
            "• Laporan = Ringkasan hari ini"
        )

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_pempek_callback(self, callback_data: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle pempek menu callbacks"""
        # Add pempek menu callback handling
        pass

    async def show_study_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show study tracking menu"""
        keyboard = [
            [
                InlineKeyboardButton("📚 TWK", callback_data="study_twk"),
                InlineKeyboardButton("🧮 TIU", callback_data="study_tiu"),
                InlineKeyboardButton("👥 TKP", callback_data="study_tkp")
            ],
            [
                InlineKeyboardButton("⏱️ Timer", callback_data="study_timer"),
                InlineKeyboardButton("📊 Progress", callback_data="study_progress")
            ],
            [InlineKeyboardButton("🔙 Menu Utama", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            "*📚 MENU BELAJAR BUMN*\n\n"
            f"Tanggal: {datetime.now().strftime('%d/%m/%Y')}\n\n"
            "Target Harian:\n"
            "• TWK: 20 soal\n"
            "• TIU: 15 soal\n"
            "• TKP: 10 soal\n\n"
            "Pilih menu untuk mulai!"
        )

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Error handler"""
        error_message = (
            "Waduh, error nih 😅\n"
            "Coba:\n"
            "1. Ketik /start\n"
            "2. Tunggu bentar\n"
            "3. Pilih menu lagi"
        )

        try:
            if update.callback_query:
                await update.callback_query.message.reply_text(error_message)
            elif update.message:
                await update.message.reply_text(error_message)
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
            
            # Add handler for unknown commands
            app.add_handler(MessageHandler(
                filters.COMMAND & ~filters.Regex("^/start$"),
                lambda u, c: u.message.reply_text("Command tidak valid! Ketik /start untuk mulai.")
            ))

            # Start bot
            print("🤖 Bot started successfully!")
            app.run_polling(allowed_updates=Update.ALL_TYPES)

        except Exception as e:
            logger.error(f"Critical error: {traceback.format_exc()}")
            raise

if __name__ == "__main__":
    bot = DimasBot()
    bot.run()
