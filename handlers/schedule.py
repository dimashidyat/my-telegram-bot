from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, time
from config import DEFAULT_SCHEDULE

class ScheduleHandler:
    def __init__(self):
        self.schedule = DEFAULT_SCHEDULE
        self.completed_tasks = set()
    
    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show schedule menu"""
        keyboard = [
            [
                InlineKeyboardButton("🌅 Jadwal Pagi", callback_data="schedule_pagi"),
                InlineKeyboardButton("☀️ Jadwal Siang", callback_data="schedule_siang")
            ],
            [
                InlineKeyboardButton("🌙 Jadwal Malam", callback_data="schedule_malam"),
                InlineKeyboardButton("✅ Progress", callback_data="schedule_progress")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        schedule_text = self._generate_schedule_overview()
        
        await update.callback_query.edit_message_text(
            f"*📅 JADWAL HARIAN*\n\n{schedule_text}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    def _generate_schedule_overview(self) -> str:
        """Generate formatted schedule overview"""
        schedule_text = ""
        current_time = datetime.now().time()
        
        for period, activities in self.schedule.items():
            schedule_text += f"*{period.title()}:*\n"
            for activity, scheduled_time in activities.items():
                status = "✅" if activity in self.completed_tasks else "⏳"
                schedule_text += f"{status} {activity.title()}: {scheduled_time.strftime('%H:%M')}\n"
            schedule_text += "\n"
        
        return schedule_text
    
    async def handle_callback(self, callback_data: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle schedule-related callbacks"""
        if callback_data == "schedule_back":
            await self.show_menu(update, context)
        elif callback_data.startswith("schedule_"):
            period = callback_data.split("_")[1]
            if period in ["pagi", "siang", "malam"]:
                await self.show_period_schedule(update, context, period)
            elif period == "progress":
                await self.show_progress(update, context) 
