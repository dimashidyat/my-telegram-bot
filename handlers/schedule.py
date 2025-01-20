from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, time
import logging
import json
import os
from config import JADWAL

logger = logging.getLogger(__name__)

class ScheduleHandler:
    def __init__(self):
        self.data = {}
        self.jadwal = JADWAL
        self.active_reminders = {}
        
        # Load existing data
        self.load_data()

    def load_data(self):
        """Load schedule data"""
        try:
            if os.path.exists('data/schedule_data.json'):
                with open('data/schedule_data.json', 'r') as f:
                    self.data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading schedule data: {e}")

    def save_data(self):
        """Save schedule data"""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/schedule_data.json', 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving schedule data: {e}")

    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show schedule menu"""
        keyboard = [
            [
                InlineKeyboardButton("📅 Jadwal Hari Ini", callback_data="schedule_today"),
                InlineKeyboardButton("⚙️ Edit Jadwal", callback_data="schedule_edit")
            ],
            [
                InlineKeyboardButton("⏰ Set Reminder", callback_data="schedule_reminder"),
                InlineKeyboardButton("📊 Progress", callback_data="schedule_progress")
            ],
            [
                InlineKeyboardButton("📝 Catatan", callback_data="schedule_notes"),
                InlineKeyboardButton("🔄 Reset", callback_data="schedule_reset")
            ],
            [InlineKeyboardButton("🔙 Menu Utama", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Get next activity
        next_activity = self.get_next_activity()

        text = (
            "*📅 JADWAL HARIAN*\n\n"
            f"🕐 Sekarang: {datetime.now().strftime('%H:%M')}\n"
            f"📍 Next: {next_activity['name']} ({next_activity['time']})\n\n"
            "*Jadwal Utama:*\n"
            "• 04.45 - Sholat Subuh\n"
            "• 07.00 - Maxim\n"
            "• 10.00 - Study BULOG\n"
            "• 12.00 - Dzuhur + Break\n"
            "• 15.00 - Ashar\n"
            "• 18.00 - Maghrib\n"
            "• 19.00 - Isya\n"
            "• 21.00 - Report Pempek\n"
            "• 22.00 - Sleep\n\n"
            "_Tips: Set reminder untuk kegiatan penting_"
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

    def get_next_activity(self) -> dict:
        """Get next scheduled activity"""
        now = datetime.now()
        current_time = now.time()
        
        # Check each period
        periods = ['pagi', 'siang', 'malam']
        for period in periods:
            for activity, activity_time in self.jadwal[period].items():
                if activity_time > current_time:
                    return {
                        'name': self.get_activity_name(activity),
                        'time': activity_time.strftime('%H:%M')
                    }
        
        # If no next activity today, return first activity tomorrow
        first_activity = list(self.jadwal['pagi'].items())[0]
        return {
            'name': self.get_activity_name(first_activity[0]),
            'time': f"Tomorrow {first_activity[1].strftime('%H:%M')}"
        }

    def get_activity_name(self, activity: str) -> str:
        """Convert activity key to readable name"""
        names = {
            'subuh': 'Sholat Subuh',
            'maxim': 'Maxim',
            'study': 'Belajar BULOG',
            'dzuhur': 'Sholat Dzuhur',
            'break': 'Istirahat',
            'ashar': 'Sholat Ashar',
            'maghrib': 'Sholat Maghrib',
            'isya': 'Sholat Isya',
            'pempek_report': 'Laporan Pempek',
            'sleep': 'Tidur'
        }
        return names.get(activity, activity.title())

    async def set_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE, activity: str):
        """Set reminder for activity"""
        user_id = str(update.effective_user.id)
        chat_id = update.effective_chat.id

        # Find activity time
        activity_time = None
        for period in self.jadwal.values():
            if activity in period:
                activity_time = period[activity]
                break

        if not activity_time:
            await update.callback_query.answer("❌ Invalid activity!")
            return

        # Schedule reminder
        job_name = f"reminder_{user_id}_{activity}"
        context.job_queue.run_daily(
            self.send_reminder,
            activity_time,
            days=(0, 1, 2, 3, 4, 5, 6),
            data={
                'activity': activity,
                'user_id': user_id
            },
            name=job_name,
            chat_id=chat_id
        )

        # Save to active reminders
        self.active_reminders[f"{user_id}_{activity}"] = {
            'activity': activity,
            'time': activity_time.strftime('%H:%M')
        }

        await update.callback_query.answer(f"✅ Reminder set for {activity} at {activity_time.strftime('%H:%M')}")

    async def send_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        """Send reminder message"""
        job = context.job
        activity = job.data['activity']
        
        message = (
            f"⏰ *REMINDER: {self.get_activity_name(activity)}*\n\n"
            f"Waktunya {self.get_activity_name(activity)}!\n"
            "_Klik_ /done _jika sudah selesai_"
        )

        await context.bot.send_message(
            chat_id=job.chat_id,
            text=message,
            parse_mode='Markdown'
        )

    async def handle_error(self, update: Update, message: str):
        """Handle errors"""
        error_text = (
            f"❌ {message}\n\n"
            "Coba:\n"
            "1. Ketik /start\n"
            "2. Pilih menu Schedule lagi\n"
            "3. Atau tunggu beberapa saat"
        )
        
        try:
            if update.callback_query:
                await update.callback_query.message.reply_text(error_text)
            else:
                await update.message.reply_text(error_text)
        except Exception as e:
            logger.error(f"Error in error handler: {e}")

    async def cleanup(self):
        """Save data before shutdown"""
        self.save_data()
