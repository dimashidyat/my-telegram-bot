from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, date
from config import GIRLFRIEND_PHONE

class RelationshipHandler:
    def __init__(self):
        self.anniversary_date = date(2021, 9, 13)
        self.gf_phone = GIRLFRIEND_PHONE
        
    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show relationship menu"""
        months = self.calculate_months()
        next_monthly = self.get_next_monthly()
        
        keyboard = [
            [
                InlineKeyboardButton("💝 Chat Sayang", url=f"https://wa.me/{self.gf_phone}"),
                InlineKeyboardButton("📅 Next Monthly", callback_data="relationship_next")
            ],
            [
                InlineKeyboardButton("💌 Love Notes", callback_data="relationship_notes"),
                InlineKeyboardButton("🎁 Gift Ideas", callback_data="relationship_gifts")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            f"*💑 STATUS RELATIONSHIP*\n\n"
            f"• Mulai pacaran: 13 September 2021\n"
            f"• Sudah jalan: {months} bulan\n"
            f"• Monthly ke-{months+1}: {next_monthly.strftime('%d %B %Y')}\n"
            f"• Sisa: {(next_monthly - date.today()).days} hari lagi\n\n"
            f"_Semoga kita bisa terus bersama ya sayang_ 💕",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    def calculate_months(self):
        """Calculate months since anniversary"""
        today = date.today()
        months = (today.year - self.anniversary_date.year) * 12 + today.month - self.anniversary_date.month
        if today.day < self.anniversary_date.day:
            months -= 1
        return months

    def get_next_monthly(self):
        """Get next monthly anniversary date"""
        today = date.today()
        if today.day >= 13:
            if today.month == 12:
                next_date = date(today.year + 1, 1, 13)
            else:
                next_date = date(today.year, today.month + 1, 13)
        else:
            next_date = date(today.year, today.month, 13)
        return next_date

    async def show_love_notes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show love notes template"""
        notes = [
            "Tetap semangat ya sayang! Aku selalu support kamu 💪",
            "Jangan lupa makan & istirahat. Love you 💕",
            "Kamu pasti bisa mencapai semua targetmu! 🎯",
            "Bangga sama progressmu hari ini 🌟"
        ]
        
        keyboard = [
            [InlineKeyboardButton("💌 Kirim Note", url=f"https://wa.me/{self.gf_phone}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            "*💌 LOVE NOTES*\n\n"
            "Template pesan buat sayang:\n\n"
            + "\n".join([f"• {note}" for note in notes]) + "\n\n"
            "_Klik tombol di bawah untuk kirim_ 💕",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_gift_ideas(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show gift ideas"""
        gifts = {
            'Mini': ['Snack favorit', 'Flower bucket kecil', 'Handwritten letter'],
            'Medium': ['Parfum', 'Skincare', 'Boneka'],
            'Special': ['Cake + flower', 'Surprise dinner', 'Couple items']
        }

        text = "*🎁 GIFT IDEAS*\n\n"
        for category, items in gifts.items():
            text += f"*{category}:*\n"
            text += "\n".join([f"• {item}" for item in items]) + "\n\n"
        
        text += "_Tips: Pilih sesuai budget, yang penting niatnya_ 💝"

        await update.callback_query.edit_message_text(
            text,
            parse_mode='Markdown'
        )  
