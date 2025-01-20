import logging
import traceback
import json
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
        self.pempek_data = {}
        self.prices = {
            'kecil': 2500,
            'gede': 12000,
            'items': {
                'air': 4000,
                'gas': 22000,
                'plastik': 2000,
                'es': 3000
            }
        }

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send main menu"""
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

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        try:
            query = update.callback_query
            await query.answer()
            user_id = str(update.effective_user.id)
            callback_data = query.data

            # Main menu navigation
            if callback_data == "back_main":
                await self.start(update, context)
                return

            # Menu selection
            if callback_data.startswith("menu_"):
                menu_type = callback_data.split("_")[1]
                self.active_menus[user_id] = menu_type
                
                if menu_type == "pempek":
                    await self.show_pempek_menu(update, context)
                elif menu_type == "study":
                    await self.show_study_menu(update, context)
                return

            # Pempek menu handlers
            if callback_data.startswith("pempek_"):
                action = callback_data.split("_")[1]
                if action == "modal":
                    await self.show_modal_input(update, context)
                elif action == "stock":
                    await self.show_stock_input(update, context)
                elif action == "setoran":
                    await self.show_setoran_input(update, context)
                elif action == "report":
                    await self.show_pempek_report(update, context)
                return

            # Modal input handlers
            if callback_data.startswith("modal_"):
                item = callback_data.split("_")[1]
                if item != "manual":
                    await self.handle_modal_input(update, context, item)
                else:
                    await self.request_manual_modal(update, context)
                return

        except Exception as e:
            logger.error(f"Error handling callback: {traceback.format_exc()}")
            await self.handle_error(update, context)

    async def show_pempek_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show pempek reporting menu"""
        user_id = str(update.effective_user.id)
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

        # Get status
        has_modal = bool(self.pempek_data.get(user_id, {}).get('modal'))
        has_stock = bool(self.pempek_data.get(user_id, {}).get('stock'))
        has_setoran = bool(self.pempek_data.get(user_id, {}).get('setoran'))

        text = (
            "*📝 MENU LAPORAN PEMPEK*\n\n"
            f"Tanggal: {datetime.now().strftime('%d/%m/%Y')}\n\n"
            "Status:\n"
            f"• Modal: {'✅' if has_modal else '❌'}\n"
            f"• Stock: {'✅' if has_stock else '❌'}\n"
            f"• Setoran: {'✅' if has_setoran else '❌'}\n\n"
            "Pilih menu untuk input data:"
        )

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_modal_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show modal input options"""
        keyboard = [
            [
                InlineKeyboardButton("💧 Air (4.000)", callback_data="modal_air"),
                InlineKeyboardButton("🔥 Gas (22.000)", callback_data="modal_gas")
            ],
            [
                InlineKeyboardButton("🛍️ Plastik (2.000)", callback_data="modal_plastik"),
                InlineKeyboardButton("🧊 Es (3.000)", callback_data="modal_es")
            ],
            [
                InlineKeyboardButton("✏️ Input Manual", callback_data="modal_manual"),
                InlineKeyboardButton("🔙 Kembali", callback_data="menu_pempek")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            "*💰 INPUT MODAL HARIAN*\n\n"
            "Pilih item atau input manual:\n\n"
            "Format input manual:\n"
            "item=harga (pisah pake koma)\n"
            "Contoh: gorengan=10000,tissue=5000"
        )

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_modal_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, item: str):
        """Process modal input"""
        try:
            user_id = str(update.effective_user.id)
            
            if user_id not in self.pempek_data:
                self.pempek_data[user_id] = {}
            
            if 'modal' not in self.pempek_data[user_id]:
                self.pempek_data[user_id]['modal'] = {}

            price = self.prices['items'].get(item)
            if price:
                self.pempek_data[user_id]['modal'][item] = price
                await update.callback_query.answer(
                    f"✅ Ditambahkan: {item} = Rp{price:,}"
                )
                await self.show_pempek_menu(update, context)

        except Exception as e:
            logger.error(f"Error in modal input: {e}")
            await self.handle_error(update, context)

    async def request_manual_modal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Request manual modal input"""
        text = (
            "*✏️ INPUT MODAL MANUAL*\n\n"
            "Ketik dengan format:\n"
            "`item=harga` (pisah pake koma)\n\n"
            "Contoh:\n"
            "`gorengan=10000,tissue=5000`\n\n"
            "Ketik /cancel untuk batal"
        )
        
        await update.callback_query.edit_message_text(
            text=text,
            parse_mode='Markdown'
        )
        
        # Set user state to expect manual input
        context.user_data['expecting_modal'] = True

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        if not context.user_data.get('expecting_modal'):
            return

        text = update.message.text
        if text == '/cancel':
            context.user_data['expecting_modal'] = False
            await self.show_pempek_menu(update, context)
            return

        try:
            # Parse manual input
            items = text.split(',')
            user_id = str(update.effective_user.id)
            
            if user_id not in self.pempek_data:
                self.pempek_data[user_id] = {'modal': {}}
                
            for item in items:
                name, price = item.split('=')
                self.pempek_data[user_id]['modal'][name.strip()] = int(price)
            
            await update.message.reply_text("✅ Modal berhasil disimpan!")
            context.user_data['expecting_modal'] = False
            
        except Exception as e:
            await update.message.reply_text(
                "❌ Format salah!\n"
                "Gunakan: item=harga,item=harga\n"
                "Contoh: gorengan=10000,tissue=5000"
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
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
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
