from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
import logging
import json

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
        
    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tampilkan menu utama pempek"""
        try:
            keyboard = [
                [
                    InlineKeyboardButton("💰 Input Modal", callback_data="pempek_modal"),
                    InlineKeyboardButton("📦 Sisa Stock", callback_data="pempek_stock")
                ],
                [
                    InlineKeyboardButton("💳 Input Setoran", callback_data="pempek_setoran"),
                    InlineKeyboardButton("📊 Laporan", callback_data="pempek_report")
                ],
                [
                    InlineKeyboardButton("📝 Review Data", callback_data="pempek_review"),
                    InlineKeyboardButton("🔄 Reset Data", callback_data="pempek_reset")
                ],
                [InlineKeyboardButton("🔙 Menu Utama", callback_data="back_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            user_id = update.effective_user.id
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
                "• Setoran = total QRIS + cash\n"
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
            logger.error(f"Error showing menu: {e}")
            await self.handle_error(update, "Ada masalah saat menampilkan menu")

    def get_input_status(self, user_id: int) -> dict:
        """Cek status input data"""
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

    async def input_modal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle input modal"""
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
            "*Pilih item atau input manual:*\n\n"
            "*Standard Items:*\n"
            "• Air = Rp4.000\n"
            "• Gas = Rp22.000\n\n"
            "*Format Manual:*\n"
            "item=harga (pisah pake koma)\n"
            "Contoh: plastik=5000, es=3000"
        )
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_modal_input(self, update: Update, item: str = None):
        """Process modal input"""
        try:
            user_id = update.effective_user.id
            
            if user_id not in self.daily_data:
                self.daily_data[user_id] = {'modal': {}}
                
            if item in self.default_prices['standard_items']:
                price = self.default_prices['standard_items'][item]
                self.daily_data[user_id]['modal'][item] = price
                
                await update.callback_query.answer(
                    f"✅ Added: {item} = Rp{price:,}"
                )
            else:
                # For manual input
                text = update.message.text
                items = [x.strip() for x in text.split(',')]
                
                for item in items:
                    name, price = item.split('=')
                    self.daily_data[user_id]['modal'][name.strip()] = int(price)
                
                await update.message.reply_text("✅ Modal berhasil disimpan!")
                
            await self.show_menu(update, None)
            
        except Exception as e:
            logger.error(f"Error handling modal input: {e}")
            await self.handle_error(update, "Format input salah")

    async def generate_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate laporan lengkap"""
        try:
            user_id = update.effective_user.id
            if user_id not in self.daily_data:
                await update.callback_query.answer(
                    "❌ Belum ada data hari ini!",
                    show_alert=True
                )
                return
                
            data = self.daily_data[user_id]
            
            # Calculate totals
            modal_total = sum(data.get('modal', {}).values())
            stock_value = sum([
                count * self.default_prices[size]
                for size, count in data.get('stock', {}).items()
            ])
            setoran_total = sum(data.get('setoran', {}).values())
            
            report = (
                f"*📊 LAPORAN PEMPEK {datetime.now().strftime('%d/%m/%Y')}*\n\n"
                "*💰 Modal Keluar:*\n"
            )
            
            # Add modal details
            for item, amount in data.get('modal', {}).items():
                report += f"• {item}: Rp{amount:,}\n"
            report += f"*Total Modal: Rp{modal_total:,}*\n\n"
            
            # Add stock details
            report += "*📦 Sisa Stock:*\n"
            for size, count in data.get('stock', {}).items():
                price = self.default_prices[size]
                report += f"• {size}: {count} pcs (Rp{count*price:,})\n"
            report += f"*Total Stock: Rp{stock_value:,}*\n\n"
            
            # Add setoran details
            report += "*💳 Setoran:*\n"
            for method, amount in data.get('setoran', {}).items():
                report += f"• {method}: Rp{amount:,}\n"
            report += f"*Total Setoran: Rp{setoran_total:,}*\n\n"
            
            # Add summary
            profit = setoran_total - modal_total
            report += (
                "*📈 Summary:*\n"
                f"• Modal: Rp{modal_total:,}\n"
                f"• Setoran: Rp{setoran_total:,}\n"
                f"• Sisa Stock: Rp{stock_value:,}\n"
                f"• *Profit: Rp{profit:,}*"
            )
            
            keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="pempek_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(
                text=report,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            await self.handle_error(update, "Gagal membuat laporan")

    async def handle_error(self, update: Update, message: str):
        """Handle errors"""
        error_text = f"❌ {message}\n\nCoba lagi atau ketik /start untuk mulai ulang"
        
        try:
            if update.callback_query:
                await update.callback_query.message.reply_text(error_text)
            else:
                await update.message.reply_text(error_text)
        except Exception as e:
            logger.error(f"Error in error handler: {e}")

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
