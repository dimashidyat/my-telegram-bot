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

    async def setup_reminders(self, application):
        """Setup daily reminders."""
        # Setup semua reminder harian
        for period, schedules in self.daily_schedule.items():
            for activity, schedule_time in schedules.items():
                application.job_queue.run_daily(
                    self.send_reminder,
                    time=schedule_time,
                    data={'activity': activity},
                    chat_id=application.bot_data['chat_id']
                )

    async def send_reminder(self, context):
        """Kirim reminder untuk aktivitas."""
        activity = context.job.data['activity']
        message = self.messages.get(activity, "⏰ Reminder!")
        
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=message
        )

    async def show_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tampilkan jadwal hari ini."""
        now = datetime.now()
        current_time = now.time()
        
        schedule_text = "📅 *JADWAL HARI INI*\n\n"
        
        # Morning schedule
        schedule_text += "*Pagi:*\n"
        schedule_text += "• 04:45 - Bangun + Subuh\n"
        schedule_text += "• 07:00 - Maxim (target: 50k)\n"
        schedule_text += "• 10:00 - Study BULOG\n\n"
        
        # Afternoon schedule
        schedule_text += "*Siang:*\n"
        schedule_text += "• 12:00 - Dzuhur\n"
        schedule_text += "• 12:30 - Break + Makan\n"
        schedule_text += "• 15:00 - Ashar\n\n"
        
        # Evening schedule
        schedule_text += "*Malam:*\n"
        schedule_text += "• 18:00 - Maghrib\n"
        schedule_text += "• 19:00 - Isya\n"
        schedule_text += "• 21:00 - Laporan Pempek\n"
        schedule_text += "• 22:00 - Persiapan Tidur\n\n"
        
        keyboard = [
            [
                InlineKeyboardButton("⏰ Set Reminder", callback_data="set_reminder"),
                InlineKeyboardButton("✏️ Edit Jadwal", callback_data="edit_schedule")
            ],
            [InlineKeyboardButton("📊 Progress Hari Ini", callback_data="daily_progress")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            schedule_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_daily_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check progress hari ini."""
        now = datetime.now()
        current_time = now.time()
        
        # Example progress check (implement with real tracking later)
        progress_text = "📊 *PROGRESS HARI INI*\n\n"
        
        # Morning tasks
        if current_time > self.daily_schedule['pagi']['subuh']:
            progress_text += "✅ Bangun pagi\n"
        else:
            progress_text += "⭕ Bangun pagi\n"
            
        if current_time > self.daily_schedule['pagi']['maxim']:
            progress_text += "✅ Maxim\n"
        else:
            progress_text += "⭕ Maxim\n"
            
        # Add other progress checks...
        
        await update.callback_query.edit_message_text(
            progress_text,
            parse_mode='Markdown'
        )

    async def edit_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Edit jadwal."""
        keyboard = [
            [InlineKeyboardButton("🌅 Edit Jadwal Pagi", callback_data="edit_morning")],
            [InlineKeyboardButton("🌞 Edit Jadwal Siang", callback_data="edit_afternoon")],
            [InlineKeyboardButton("🌙 Edit Jadwal Malam", callback_data="edit_evening")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            "Pilih jadwal yang mau diedit:",
            reply_markup=reply_markup
        )

    async def set_custom_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set reminder custom."""
        keyboard = [
            [
                InlineKeyboardButton("⏰ 5 menit", callback_data="remind_5"),
                InlineKeyboardButton("⏰ 15 menit", callback_data="remind_15"),
                InlineKeyboardButton("⏰ 30 menit", callback_data="remind_30")
            ],
            [InlineKeyboardButton("🔄 Set Manual", callback_data="remind_manual")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            "Mau diingetin dalam berapa menit?",
            reply_markup=reply_markup
