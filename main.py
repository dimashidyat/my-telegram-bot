from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
import logging
import json
import os
from config import PEMPEK_PRICES

logger = logging.getLogger(__name__)

class PempekHandler:
    def __init__(self):
        self.data = {}
        self.prices = PEMPEK_PRICES
        self.hari = {
            0: 'Senin',
            1: 'Selasa', 
            2: 'Rabu',
            3: 'Kamis',
            4: 'Jumat',
            5: 'Sabtu',
            6: 'Minggu'
        }
        
        # Load existing data
        self.load_data()

    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main pempek menu"""
        keyboard = [
            [
                InlineKeyboardButton("1️⃣ Input Pengeluaran", callback_data="pempek_pengeluaran"),
                InlineKeyboardButton("2️⃣ Input Sisa", callback_data="pempek_sisa")
            ],
            [
                InlineKeyboardButton("3️⃣ Input Setoran", callback_data="pempek_setoran"),
                InlineKeyboardButton("4️⃣ Input Plastik", callback_data="pempek_plastik")
            ],
            [
                InlineKeyboardButton("📊 Generate Laporan", callback_data="pempek_report"),
                InlineKeyboardButton("🔄 Reset", callback_data="pempek_reset")
            ],
            [InlineKeyboardButton("🔙 Menu Utama", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Get status
        user_id = str(update.effective_user.id)
        status = self.get_status(user_id)
        
        text = (
            f"*📝 LAPORAN {self.get_date_string()}*\n\n"
            "*Status Input:*\n"
            f"1️⃣ Pengeluaran: {status['pengeluaran']}\n"
            f"2️⃣ Sisa Pempek: {status['sisa']}\n"
            f"3️⃣ Setoran: {status['setoran']}\n"
            f"4️⃣ Sisa Plastik: {status['plastik']}\n\n"
            "_Pilih menu untuk input data_"
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

    async def handle_pengeluaran(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle pengeluaran input"""
        keyboard = [
            [
                InlineKeyboardButton("💧 Air (4.000)", callback_data="pengeluaran_air"),
                InlineKeyboardButton("🔥 Gas (22.000)", callback_data="pengeluaran_gas")
            ],
            [
                InlineKeyboardButton("👤 Dimas", callback_data="pengeluaran_dimas"),
                InlineKeyboardButton("✏️ Input Manual", callback_data="pengeluaran_manual")
            ],
            [InlineKeyboardButton("🔙 Kembali", callback_data="menu_pempek")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            "*1️⃣ INPUT PENGELUARAN*\n\n"
            "Pilih item atau input manual:\n\n"
            "Format manual:\n"
            "`nama=harga`\n"
            "Contoh: `doubletip=5000`"
        )

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_sisa_pempek(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle sisa pempek input"""
        keyboard = [
            [InlineKeyboardButton("🟡 Input Pempek Kecil", callback_data="sisa_kecil")],
            [InlineKeyboardButton("🔵 Input Pempek Gede", callback_data="sisa_gede")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="menu_pempek")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            "*2️⃣ INPUT SISA PEMPEK*\n\n"
            "*Harga per pcs:*\n"
            "• Kecil = Rp2.500\n"
            "• Gede = Rp12.000\n\n"
            "Format: ketik angka saja\n"
            "Contoh: `36`"
        )

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_setoran(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle setoran input"""
        keyboard = [
            [
                InlineKeyboardButton("💳 Input QRIS", callback_data="setoran_qris"),
                InlineKeyboardButton("💵 Input Cash", callback_data="setoran_cash")
            ],
            [InlineKeyboardButton("🔙 Kembali", callback_data="menu_pempek")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            "*3️⃣ INPUT SETORAN*\n\n"
            "Pilih metode pembayaran:\n\n"
            "Format: ketik angka saja\n"
            "Contoh: `1040000`"
        )

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_plastik(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle plastik input"""
        keyboard = [
            [InlineKeyboardButton("1/4", callback_data="plastik_14")],
            [InlineKeyboardButton("1/2", callback_data="plastik_12")],
            [InlineKeyboardButton("1", callback_data="plastik_1")],
            [InlineKeyboardButton("Kantong", callback_data="plastik_kantong")],
            [InlineKeyboardButton("🛢️ Status Minyak", callback_data="plastik_minyak")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="menu_pempek")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            "*4️⃣ INPUT SISA PLASTIK*\n\n"
            "Format input:\n"
            "`baik=rusak`\n"
            "Contoh: `3=1`"
        )

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def generate_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate formatted report"""
        user_
