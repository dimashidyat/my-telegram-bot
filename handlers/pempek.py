from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

class PempekHandler:
    def __init__(self):
        self.template = {
            'pengeluaran': {},
            'sisa': {'kecil': 0, 'gede': 0},
            'setoran': {'qris': 0, 'cash': 0}
        }
        
    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show pempek report menu"""
        keyboard = [
            [
                InlineKeyboardButton("💰 Input Modal", callback_data="pempek_modal"),
                InlineKeyboardButton("📦 Sisa Stock", callback_data="pempek_sisa")
            ],
            [
                InlineKeyboardButton("💳 Input Setoran", callback_data="pempek_setoran"),
                InlineKeyboardButton("📊 Laporan", callback_data="pempek_report")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            "📝 *MENU LAPORAN PEMPEK*\n\n"
            "Pilih yang mau diinput:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_modal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle modal input"""
        await update.callback_query.message.reply_text(
            "*💰 INPUT MODAL*\n\n"
            "Format input:\n"
            "item=harga (pisah pake koma)\n\n"
            "Contoh: air=4000, gas=22000\n\n"
            "Item rutin:\n"
            "• Air = 4.000\n"
            "• Gas = 22.000\n"
            "• Minyak = sesuai kebutuhan",
            parse_mode='Markdown'
        )

    async def handle_sisa(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle sisa stock input"""
        await update.callback_query.message.reply_text(
            "*📦 SISA STOCK*\n\n"
            "Format input:\n"
            "jenis=jumlah (pisah pake koma)\n\n"
            "Contoh: kecil=5, gede=3\n\n"
            "Harga:\n"
            "• Kecil = Rp2.500\n"
            "• Gede = Rp12.000",
            parse_mode='Markdown'
        )

    async def handle_setoran(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle setoran input"""
        await update.callback_query.message.reply_text(
            "*💳 INPUT SETORAN*\n\n"
            "Format input:\n"
            "metode=jumlah (pisah pake koma)\n\n"
            "Contoh: qris=50000, cash=100000",
            parse_mode='Markdown'
        )

    async def generate_report(self, data: dict) -> str:
        """Generate complete report"""
        total_modal = sum(data['pengeluaran'].values())
        total_sisa = (data['sisa']['kecil'] * 2500) + (data['sisa']['gede'] * 12000)
        total_setoran = data['setoran']['qris'] + data['setoran']['cash']
        profit = total_setoran - total_modal

        report = f"""
📊 *LAPORAN PEMPEK {datetime.now().strftime('%d/%m/%Y')}*

💰 *Modal Keluar:*
"""
        for item, amount in data['pengeluaran'].items():
            report += f"• {item}: Rp{amount:,}\n"
        report += f"*Total Modal: Rp{total_modal:,}*\n\n"

        report += "📦 *Sisa Dagangan:*\n"
        report += f"• Kecil: {data['sisa']['kecil']} pcs (Rp{data['sisa']['kecil']*2500:,})\n"
        report += f"• Gede: {data['sisa']['gede']} pcs (Rp{data['sisa']['gede']*12000:,})\n"
        report += f"*Total Sisa: Rp{total_sisa:,}*\n\n"

        report += "💳 *Setoran:*\n"
        report += f"• QRIS: Rp{data['setoran']['qris']:,}\n"
        report += f"• Cash: Rp{data['setoran']['cash']:,}\n"
        report += f"*Total Setoran: Rp{total_setoran:,}*\n\n"

        report += "📈 *Summary:*\n"
        report += f"• Modal: Rp{total_modal:,}\n"
        report += f"• Setoran: Rp{total_setoran:,}\n"
        report += f"• Profit: Rp{profit:,}"

        return report
