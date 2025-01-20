from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, time

class ScheduleHandler:
    def __init__(self):
        # Jadwal default
        self.daily_schedule = {
            'pagi': {
                'subuh': time(4, 45),  # Bangun + Subuh
                'maxim': time(7, 0),   # Mulai Maxim
                'study': time(10, 0)   # Belajar BULOG
            },
            'siang': {
                'dzuhur': time(12, 0),
                'break': time(12, 30),  # Istirahat
                'ashar': time(15, 0)
            },
            'malam': {
                'maghrib': time(18, 0),
                'isya': time(19, 0),
                'pempek': time(21, 0),  # Laporan pempek
                'sleep': time(22, 0)    # Target tidur
            }
        }

        # Template reminder messages
        self.messages = {
            'subuh': "🌅 Waktunya bangun bro!\nJangan telat subuh ya...",
            'maxim': "🛵 Gas Maxim dulu, target 50k!",
            'study': "📚 Break Maxim, saatnya belajar BULOG",
            'break': "🍱 Istirahat dulu bro, jangan lupa makan",
            'pempek': "📝 Reminder: Input laporan pempek hari ini!",
            'sleep': "😴 Udah malem bro, besok pagi ada Maxim"
        }

    async def show_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tampilkan jadwal hari ini."""
        await update.callback_query.edit_message_text(
            "📅 *JADWAL HARI INI*\n\n"
            "*Pagi:*\n"
            "• 04:45 - Bangun + Subuh\n"
            "• 07:00 - Maxim (target: 50k)\n"
            "• 10:00 - Study BULOG\n\n"
            "*Siang:*\n"
            "• 12:00 - Dzuhur\n"
            "• 12:30 - Break + Makan\n"
            "• 15:00 - Ashar\n\n"
            "*Malam:*\n"
            "• 18:00 - Maghrib\n"
            "• 19:00 - Isya\n"
            "• 21:00 - Laporan Pempek\n"
            "• 22:00 - Persiapan Tidur\n\n",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⏰ Set Reminder", callback_data="set_reminder"),
                    InlineKeyboardButton("✏ Edit Jadwal", callback_data="edit_schedule")
                ],
                [InlineKeyboardButton("📊 Progress Hari Ini", callback_data="daily_progress")]
            ]),
            parse_mode='Markdown'
        )
