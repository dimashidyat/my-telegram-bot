import logging
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import PEMPEK_PRICES

logger = logging.getLogger(__name__)

class PempekHandler:
    def __init__(self):
        self.data = {}
        self.prices = PEMPEK_PRICES

    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main pempek menu"""
        user_id = str(update.effective_user.id)
        keyboard = [
            [
                InlineKeyboardButton("💰 Pengeluaran", callback_data="pempek_pengeluaran"),
                InlineKeyboardButton("📦 Stok", callback_data="pempek_stok")
            ],
            [
                InlineKeyboardButton("💵 Pemasukan", callback_data="pempek_pemasukan"),
                InlineKeyboardButton("📊 Laporan", callback_data="pempek_laporan")
            ],
            [InlineKeyboardButton("🔙 Menu Utama", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Check status
        status = self.get_status(user_id)
        
        text = (
            "*📝 LAPORAN PEMPEK*\n\n"
            f"📅 Tanggal: {datetime.now().strftime('%d/%m/%Y')}\n\n"
            "Status Input:\n"
            f"• Pengeluaran: {status['pengeluaran']}\n"
            f"• Stok: {status['stok']}\n" 
            f"• Pemasukan: {status['pemasukan']}\n\n"
            "Pilih menu untuk mulai:"
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

    async def handle_callback(self, callback_data: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle pempek menu callbacks"""
        user_id = str(update.effective_user.id)
        action = callback_data.split('_')[1]

        handlers = {
            'pengeluaran': self.show_pengeluaran_menu,
            'stok': self.show_stok_menu,
            'pemasukan': self.show_pemasukan_menu,
            'laporan': self.show_laporan
        }

        if action in handlers:
            await handlers[action](update, context)
        elif callback_data.startswith('input_'):
            await self.handle_input(update, context, callback_data)

    async def show_pengeluaran_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show pengeluaran input menu"""
        keyboard = [
            [
                InlineKeyboardButton("💧 Air Galon (4.000)", callback_data="input_air"),
                InlineKeyboardButton("🔥 Gas (22.000)", callback_data="input_gas")
            ],
            [
                InlineKeyboardButton("🛍️ Plastik (2.000)", callback_data="input_plastik"),
                InlineKeyboardButton("🧊 Es Batu (3.000)", callback_data="input_es")
            ],
            [
                InlineKeyboardButton("✏️ Input Manual", callback_data="input_manual"),
                InlineKeyboardButton("🔙 Kembali", callback_data="menu_pempek")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            "*💰 INPUT PENGELUARAN*\n\n"
            "Pilih item atau input manual:\n\n"
            "Format input manual:\n"
            "item=jumlah=harga\n"
            "Contoh: plastik=2=4000"
        )

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, input_data: str):
        """Process input data"""
        user_id = str(update.effective_user.id)
        item = input_data.split('_')[1]

        if user_id not in self.data:
            self.data[user_id] = {}

        if item in self.prices['bahan']:
            item_data = self.prices['bahan'][item]
            self.data[user_id][item] = {
                'nama': item_data['nama'],
                'harga': item_data['harga'],
                'jumlah': 1,
                'total': item_data['harga']
            }
            await update.callback_query.answer(
                f"✅ {item_data['nama']}: Rp{item_data['harga']:,}"
            )
            await self.show_menu(update, context)

    def get_status(self, user_id: str) -> dict:
        """Get input status"""
        if user_id not in self.data:
            return {
                'pengeluaran': '❌ Belum',
                'stok': '❌ Belum',
                'pemasukan': '❌ Belum'
            }

        data = self.data[user_id]
        return {
            'pengeluaran': '✅ Sudah' if data.get('pengeluaran') else '❌ Belum',
            'stok': '✅ Sudah' if data.get('stok') else '❌ Belum',
            'pemasukan': '✅ Sudah' if data.get('pemasukan') else '❌ Belum'
        }

    def save_data(self):
        """Save data to file"""
        with open('data/pempek.json', 'w') as f:
            json.dump(self.data, f)

    def load_data(self):
        """Load data from file"""
        try:
            with open('data/pempek.json', 'r') as f:
                self.data = json.load(f)
        except:
            self.data = {}
