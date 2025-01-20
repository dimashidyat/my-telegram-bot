from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, time
import logging
import json
import os
from config import HEALTH_GOALS

logger = logging.getLogger(__name__)

class HealthHandler:
    def __init__(self):
        self.data = {}
        self.goals = HEALTH_GOALS
        self.active_workouts = {}
        
        # Load data
        self.load_data()
        
    def load_data(self):
        """Load health data"""
        try:
            if os.path.exists('data/health_data.json'):
                with open('data/health_data.json', 'r') as f:
                    self.data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading health data: {e}")
            
    def save_data(self):
        """Save health data"""
        try:
            with open('data/health_data.json', 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving health data: {e}")

    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show health menu"""
        keyboard = [
            [
                InlineKeyboardButton("💪 Quick Workout", callback_data="health_workout"),
                InlineKeyboardButton("😴 Sleep Track", callback_data="health_sleep")
            ],
            [
                InlineKeyboardButton("📊 Progress", callback_data="health_progress"),
                InlineKeyboardButton("🎯 Set Target", callback_data="health_target")
            ],
            [
                InlineKeyboardButton("💧 Water", callback_data="health_water"),
                InlineKeyboardButton("⚖️ Weight", callback_data="health_weight")
            ],
            [InlineKeyboardButton("🔙 Menu Utama", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        user_id = str(update.effective_user.id)
        stats = self.get_user_stats(user_id)

        text = (
            "*💪 HEALTH TRACKER*\n\n"
            "*Progress Hari Ini:*\n"
            f"• Workout: {stats['workout']}/{self.goals['workout']['target']} {self.goals['workout']['unit']}\n"
            f"• Sleep: {stats['sleep']}/{self.goals['sleep']['target']} {self.goals['sleep']['unit']}\n"
            f"• Water: {stats['water']}/{self.goals['water']['target']} {self.goals['water']['unit']}\n\n"
            f"🔥 Streak: {stats['streak']} hari\n\n"
            "*Quick Workout Ideas:*\n"
            "• Morning: 5-10 min exercise\n"
            "• Break: Office stretching\n"
            "• Night: Light yoga\n\n"
            "_Tips: Konsisten > Intense_"
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

    async def handle_workout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle workout menu"""
        keyboard = [
            [
                InlineKeyboardButton("🌅 Morning (5-10m)", callback_data="workout_morning"),
                InlineKeyboardButton("🏃 Full (20-30m)", callback_data="workout_full")
            ],
            [
                InlineKeyboardButton("🧘‍♂️ Break Exercise", callback_data="workout_break"),
                InlineKeyboardButton("🌙 Night Stretch", callback_data="workout_night")
            ],
            [InlineKeyboardButton("🔙 Kembali", callback_data="health_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            "*💪 QUICK WORKOUT*\n\n"
            "*Pilih workout:*\n\n"
            "1️⃣ Morning Workout\n"
            "• Push up 5-10x\n"
            "• Plank 20-30s\n"
            "• Squat 10x\n\n"
            "2️⃣ Full Workout\n"
            "• Push up 3 set\n"
            "• Plank 1 min\n"
            "• Squat 3 set\n\n"
            "3️⃣ Break Exercise\n"
            "• Office stretching\n"
            "• Light movement\n\n"
            "4️⃣ Night Stretch\n"
            "• Light yoga\n"
            "• Relaxation\n\n"
            "_Pilih sesuai waktu & tenaga!_"
        )

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_sleep(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle sleep tracking"""
        keyboard = [
            [
                InlineKeyboardButton("😴 Sleep Now", callback_data="sleep_start"),
                InlineKeyboardButton("⏰ Wake Up", callback_data="sleep_end")
            ],
            [
                InlineKeyboardButton("📊 Sleep Stats", callback_data="sleep_stats"),
                InlineKeyboardButton("⚙️ Set Reminder", callback_data="sleep_reminder")
            ],
            [InlineKeyboardButton("🔙 Kembali", callback_data="health_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        user_id = str(update.effective_user.id)
        stats = self.get_sleep_stats(user_id)

        text = (
            "*😴 SLEEP TRACKER*\n\n"
            "*Schedule:*\n"
            "• Target tidur: 22:00\n"
            "• Target bangun: 04:45\n\n"
            "*Progress Minggu Ini:*\n"
            f"• Rata-rata: {stats['average']} jam\n"
            f"• Best streak: {stats['best_streak']} hari\n"
            f"• Current: {stats['current_streak']} hari\n\n"
            "_Tips: Konsisten jam tidur > Durasi_"
        )

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    def get_user_stats(self, user_id: str) -> dict:
        """Get user health statistics"""
        if user_id not in self.data:
            return {
                'workout': 0,
                'sleep': 0,
                'water': 0,
                'streak': 0,
                'weight': None
            }
