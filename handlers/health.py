from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

class HealthHandler:
    def __init__(self):
        self.health_data = {}
        self.goals = {
            'workout': {'target': 30, 'unit': 'menit'},
            'sleep': {'target': 6, 'unit': 'jam'},
            'water': {'target': 2, 'unit': 'liter'}
        }

    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show health tracking menu"""
        keyboard = [
            [
                InlineKeyboardButton("💪 Log Workout", callback_data="health_workout"),
                InlineKeyboardButton("😴 Log Tidur", callback_data="health_sleep")
            ],
            [
                InlineKeyboardButton("🏋 Tips Olahraga", callback_data="health_tips"),
                InlineKeyboardButton("📊 Progress", callback_data="health_progress")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            "*💪 HEALTH TRACKER*\n\n"
            "*Target Hari Ini:*\n"
            "• Workout: 30 menit\n"
            "• Tidur: 6 jam\n"
            "• Minum: 2 liter\n\n"
            "*Tips Simple:*\n"
            "• Push up tiap sholat\n"
            "• Jalan pas cari order\n"
            "• Tidur max 22:00\n",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
