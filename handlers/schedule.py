from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, time, timedelta
import logging
from config import DEFAULT_SCHEDULE

logger = logging.getLogger(__name__)

class ScheduleHandler:
    def __init__(self):
        self.schedules = {}  # Untuk menyimpan jadwal custom per user
        self.reminders = {}  # Untuk menyimpan reminder aktif
        self.default_schedule = DEFAULT_SCHEDULE

    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tampilkan menu jadwal"""
        try:
            user_id = update.effective_user.id
            now = datetime.now()
            current_time = now.time()

            # Initialize user schedule if needed
            if user_id not in self.schedules:
                self.schedules[user_id] = self.default_schedule.copy()

            keyboard = [
                [
                    InlineKeyboardButton("📅 Lihat Jadwal", callback_data="schedule_view"),
                    InlineKeyboardButton("⚙️ Edit Jadwal", callback_data="schedule_edit")
                ],
                [
                    InlineKeyboardButton("⏰ Set Reminder", callback_data="schedule_reminder"),
                    InlineKeyboardButton("📊 Progress", callback_data="schedule_progress")
                ],
                [InlineKeyboardButton("🔙 Menu Utama", callback_data="back_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Get next activity
            next_activity = self.get_next_activity(user_id)

            text = (
                "*⏰ JADWAL HARIAN*\n\n"
                f"🕐 Sekarang: {now.strftime('%H:%M')}\n"
            )

            if next_activity:
                activity, act_time = next_activity
                text += f"📍 Next: {activity} ({act_time.strftime('%H:%M')})\n"
            
            text += "\n*Quick Menu:*\n• Lihat jadwal lengkap\n• Edit waktu aktivitas\n• Set pengingat baru"

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
            logger.error(f"Error in show_menu: {e}")
            await self.handle_error(update, "Gagal menampilkan menu jadwal")

    async def view_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tampilkan jadwal lengkap"""
        try:
            user_id = update.effective_user.id
            schedule = self.schedules.get(user_id, self.default_schedule)
            
            text = "*📅 JADWAL LENGKAP*\n\n"
            
            # Morning schedule
            text += "*Pagi:*\n"
            for activity, act_time in schedule['pagi'].items():
                text += f"• {act_time.strftime('%H:%M')} - {self.get_activity_name(activity)}\n"
            
            # Afternoon schedule
            text += "\n*Siang:*\n"
            for activity, act_time in schedule['siang'].items():
                text += f"• {act_time.strftime('%H:%M')} - {self.get_activity_name(activity)}\n"
            
            # Night schedule
            text += "\n*Malam:*\n"
            for activity, act_time in schedule['malam'].items():
                text += f"• {act_time.strftime('%H:%M')} - {self.get_activity_name(activity)}\n"

            keyboard = [
                [
                    InlineKeyboardButton("⚙️ Edit Jadwal", callback_data="schedule_edit"),
                    InlineKeyboardButton("⏰ Set Reminder", callback_data="schedule_reminder")
                ],
                [InlineKeyboardButton("🔙 Kembali", callback_data="schedule_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error viewing schedule: {e}")
            await self.handle_error(update, "Gagal menampilkan jadwal")

    def get_activity_name(self, activity_key: str) -> str:
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
        return names.get(activity_key, activity_key.title())

    def get_next_activity(self, user_id: int) -> tuple:
        """Get next scheduled activity"""
        try:
            schedule = self.schedules.get(user_id, self.default_schedule)
            now = datetime.now().time()
            
            # Flatten schedule
            all_activities = []
            for period in ['pagi', 'siang', 'malam']:
                for activity, act_time in schedule[period].items():
                    if act_time > now:
                        all_activities.append((activity, act_time))
            
            if all_activities:
                return min(all_activities, key=lambda x: x[1])
            return None

        except Exception as e:
            logger.error(f"Error getting next activity: {e}")
            return None

    async def set_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE, activity: str, remind_time: time):
        """Set reminder for activity"""
        try:
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id
            
            # Calculate delay until reminder
            now = datetime.now()
            remind_datetime = datetime.combine(now.date(), remind_time)
            
            if remind_datetime < now:
                remind_datetime += timedelta(days=1)
            
            delay = (remind_datetime - now).total_seconds()
            
            # Schedule reminder
            context.job_queue.run_once(
                self.send_reminder,
                delay,
                context={
                    'user_id': user_id,
                    'chat_id': chat_id,
                    'activity': activity
                },
                name=f"reminder_{user_id}_{activity}"
            )
            
            await update.callback_query.answer(f"Reminder set for {activity} at {remind_time.strftime('%H:%M')}")

        except Exception as e:
            logger.error(f"Error setting reminder: {e}")
            await self.handle_error(update, "Gagal mengatur reminder")

    async def send_reminder(self, context):
        """Send reminder notification"""
        try:
            job = context.job
            activity = job.context['activity']
            chat_id = job.context['chat_id']
            
            remind_text = (
                f"⏰ *REMINDER!*\n\n"
                f"Waktunya {self.get_activity_name(activity)}!\n"
                "Jangan lupa ya..."
            )
            
            keyboard = [[InlineKeyboardButton("✅ Done", callback_data=f"remind_done_{activity}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=remind_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error sending reminder: {e}")

    async def handle_error(self, update: Update, message: str):
        """Handle errors"""
        error_text = (
            f"❌ {message}\n\n"
            "Coba:\n"
            "1. Ketik /start\n"
            "2. Pilih menu Jadwal lagi"
        )
        
        if update.callback_query:
            await update.callback_query.message.reply_text(error_text)
        else:
            await update.message.reply_text(error_text)
