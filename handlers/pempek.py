from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
import logging
import json
from datetime import datetime

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

class PempekHandler:
    def __init__(self):
        self.daily_data = {}
        self.default_prices = {
            'kecil': 2500,
            'gede': 12000,
            'standard_items': {
                'air': 4000,
                'gas': 22000
            }
        }

    async def setup_handlers(self, application: Application):
        """Setup all handlers"""
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries"""
        query = update.callback_query
        await query.answer()  # Always answer callback query first

        if query.data == "pempek_menu":
            await self.show_menu(update, context)
        elif query.data == "pempek_modal":
            await self.input_modal(update, context)
        elif query.data == "pempek_stock":
            await self.input_stock(update, context)
        elif query.data == "pempek_setoran":
            await self.input_setoran(update, context)
        elif query.data == "pempek_report":
            await self.generate_report(update, context)
        elif query.data.startswith("modal_"):
            item = query.data.split("_")[1]
            await self.handle_modal_input(update, item)

    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main pempek menu"""
        keyboard = [
            [
                InlineKeyboardButton("💰 Input Modal", callback_data="pempek_modal"),
                InlineKeyboardButton("📦 Sisa Stock", callback_data="pempek_stock")
            ],
            [
                InlineKeyboardButton("💳 Input Setoran", callback_data="pempek_setoran"),
                InlineKeyboardButton("📊 Laporan", callback_data="pempek_report")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        user_id = str(update.effective_user.id)
        status = self.get_input_status(user_id)

        text = (
            "*📝 MENU LAPORAN PEMPEK*\n\n"
            "*Status Input:*\n"
            f"• Modal: {status['modal']}\n"
            f"• Stock: {status['stock']}\n"
            f"• Setoran: {status['setoran']}\n\n"
            "*Tips:*\n"
            "• Input modal = pengeluaran hari ini\n"
            "• Stock = sisa dagangan (kecil/gede)\n"
            "• Setoran = total QRIS + cash"
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

    async def input_modal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle modal input interface"""
        keyboard = [
            [
                InlineKeyboardButton("💧 Air (4.000)", callback_data="modal_air"),
                InlineKeyboardButton("🔥 Gas (22.000)", callback_data="modal_gas")
            ],
            [
                InlineKeyboardButton("🛍️ Input Manual", callback_data="modal_manual"),
                InlineKeyboardButton("🔙 Kembali", callback_data="pempek_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            "*💰 INPUT MODAL*\n\n"
            "Pilih item atau input manual:\n\n"
            "*Standard Items:*\n"
            "• Air = Rp4.000\n"
            "• Gas = Rp22.000\n\n"
            "*Format Manual:*\n"
            "Ketik: item=harga (pisah pake koma)\n"
            "Contoh: plastik=5000, es=3000"
        )

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    def get_input_status(self, user_id: str) -> dict:
        """Get current input status"""
        if user_id not in self.daily_data:
            return {
                'modal': '❌ Belum',
                'stock': '❌ Belum',
                'setoran': '❌ Belum'
            }

        data = self.daily_data[user_id]
        return {
            'modal': '✅ Sudah' if data.get('modal') else '❌ Belum',
            'stock': '✅ Sudah' if data.get('stock') else '❌ Belum',
            'setoran': '✅ Sudah' if data.get('setoran') else '❌ Belum'
        }

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        text = update.message.text.lower()
        
        if "=" in text and "," in text:  # Likely a manual modal input
            await self.handle_modal_input(update)
        else:
            # Handle other message types or return to menu
            await self.show_menu(update, context)

    def save_data(self):
        """Save data to file"""
        try:
            with open('pempek_data.json', 'w') as f:
                json.dump(self.daily_data, f)
        except Exception as e:
            logger.error(f"Error saving data: {e}")

    def load_data(self):
        """Load data from file"""
        try:
            with open('pempek_data.json', 'r') as f:
                self.daily_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.daily_data = {}
