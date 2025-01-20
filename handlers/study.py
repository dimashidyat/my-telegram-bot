from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
from config import CHANNELS, STUDY_MATERIALS

class StudyHandler:
    def __init__(self):
        self.progress = {}
        self.targets = {
            'TWK': 20,
            'TIU': 15,
            'TKP': 10
        }

    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show study menu"""
        keyboard = [
            [
                InlineKeyboardButton("📚 TWK", callback_data="study_twk"),
                InlineKeyboardButton("🧮 TIU", callback_data="study_tiu"),
                InlineKeyboardButton("👥 TKP", callback_data="study_tkp")
            ],
            [
                InlineKeyboardButton("⏰ Timer", callback_data="study_timer"),
                InlineKeyboardButton("📊 Progress", callback_data="study_progress")
            ],
            [InlineKeyboardButton("📱 Join Channel BUMN", url=f"https://t.me/{CHANNELS['bumn']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            "*📚 MENU BELAJAR BULOG*\n\n"
            "*Progress Hari Ini:*\n"
            f"• TWK: 0/{self.targets['TWK']} soal\n"
            f"• TIU: 0/{self.targets['TIU']} soal\n"
            f"• TKP: 0/{self.targets['TKP']} soal\n\n"
            "*Tips:*\n"
            "• Fokus TWK dulu (20 soal/hari)\n"
            "• Break tiap 25 menit\n"
            "• Join channel untuk update soal",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_timer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show study timer options"""
        keyboard = [
            [
                InlineKeyboardButton("⏰ 25 min", callback_data="timer_25"),
                InlineKeyboardButton("⏰ 45 min", callback_data="timer_45")
            ],
            [InlineKeyboardButton("⏰ Custom", callback_data="timer_custom")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            "*⏰ STUDY TIMER*\n\n"
            "Pilih durasi belajar:\n\n"
            "*Rekomendasi:*\n"
            "• 25 min = 1 sesi Pomodoro\n"
            "• 45 min = Deep work session\n"
            "• Custom = Set sendiri\n\n"
            "Tips: Break 5 menit tiap sesi!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show study progress"""
        user_id = update.effective_user.id
        today = datetime.now().strftime('%Y-%m-%d')

        if user_id not in self.progress:
            self.progress[user_id] = {
                'TWK': 0,
                'TIU': 0,
                'TKP': 0,
                'study_time': 0
            }

        progress = self.progress[user_id]
        
        text = f"""
📊 *PROGRESS BELAJAR*

*Hari ini ({today}):*
• TWK: {progress['TWK']}/{self.targets['TWK']} soal
• TIU: {progress['TIU']}/{self.targets['TIU']} soal
• TKP: {progress['TKP']}/{self.targets['TKP']} soal

⏱ *Total Waktu Belajar:*
{progress['study_time']} menit

*Tips Belajar:*
• Fokus quality > quantity
• Review kesalahan
• Catat rumus & keywords
"""
        await update.callback_query.edit_message_text(
            text,
            parse_mode='Markdown'
        ) 
