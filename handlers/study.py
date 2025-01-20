import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import STUDY_MATERIALS

logger = logging.getLogger(__name__)

class StudyHandler:
    def __init__(self):
        self.study_data = {}
        self.targets = {
            'TWK': 20,
            'TIU': 15,
            'TKP': 10
        }

    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main study menu"""
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
            [
                InlineKeyboardButton("📝 Notes", callback_data="study_notes"),
                InlineKeyboardButton("🎯 Target", callback_data="study_target")
            ],
            [InlineKeyboardButton("🔙 Menu Utama", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        user_id = str(update.effective_user.id)
        stats = self.get_daily_stats(user_id)

        text = (
            "*📚 MENU BELAJAR BULOG*\n\n"
            f"📅 {datetime.now().strftime('%d/%m/%Y')}\n\n"
            "Progress Hari Ini:\n"
            f"• TWK: {stats['TWK']}/{self.targets['TWK']} soal\n"
            f"• TIU: {stats['TIU']}/{self.targets['TIU']} soal\n"
            f"• TKP: {stats['TKP']}/{self.targets['TKP']} soal\n\n"
            f"⏱️ Total waktu: {stats['study_time']} menit\n\n"
            "Tips:\n"
            "• TWK = Latihan soal NKRI\n"
            "• TIU = Fokus logika & analisis\n"
            "• TKP = Kasus & karakteristik PNS"
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
        """Handle study menu callbacks"""
        action = callback_data.split('_')[1]

        handlers = {
            'twk': self.show_twk_menu,
            'tiu': self.show_tiu_menu,
            'tkp': self.show_tkp_menu,
            'timer': self.show_timer_menu,
            'progress': self.show_progress,
            'notes': self.show_notes,
            'target': self.show_target
        }

        if action in handlers:
            await handlers[action](update, context)
        elif callback_data.startswith('timer_'):
            duration = callback_data.split('_')[1]
