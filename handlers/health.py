from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class HealthHandler:
    def __init__(self):
        self.health_data = {}
        self.goals = {
            'workout': {'target': 30, 'unit': 'menit'},
            'sleep': {'target': 6, 'unit': 'jam'},
            'water': {'target': 2, 'unit': 'liter'}
        }
        self.workout_options = {
            'pushup': {'calories': 100, 'difficulty': 'medium'},
            'plank': {'calories': 50, 'difficulty': 'easy'},
            'squat': {'calories': 150, 'difficulty': 'medium'},
            'running': {'calories': 200, 'difficulty': 'hard'}
        }

    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tampilkan menu health tracking"""
        try:
            keyboard = [
                [
                    InlineKeyboardButton("💪 Log Workout", callback_data="health_workout"),
                    InlineKeyboardButton("😴 Log Tidur", callback_data="health_sleep")
                ],
                [
                    InlineKeyboardButton("💧 Log Air", callback_data="health_water"),
                    InlineKeyboardButton("📊 Progress", callback_data="health_progress")
                ],
                [
                    InlineKeyboardButton("🎯 Set Target", callback_data="health_goals"),
                    InlineKeyboardButton("📋 Tips", callback_data="health_tips")
                ],
                [InlineKeyboardButton("🔙 Menu Utama", callback_data="back_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            user_id = update.effective_user.id
            progress = self.get_daily_progress(user_id)
            
            text = (
                "*💪 HEALTH TRACKER*\n\n"
                "*Progress Hari Ini:*\n"
                f"• Workout: {progress['workout']}/{self.goals['workout']['target']} {self.goals['workout']['unit']}\n"
                f"• Tidur: {progress['sleep']}/{self.goals['sleep']['target']} {self.goals['sleep']['unit']}\n"
                f"• Air: {progress['water']}/{self.goals['water']['target']} {self.goals['water']['unit']}\n\n"
                "*Quick Tips:*\n"
                "• Push up setiap habis sholat\n"
                "• Bawa botol minum kemana-mana\n"
                "• Tidur max jam 10 malem"
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

        except Exception as e:
            logger.error(f"Error in show_menu: {e}")
            await self.handle_error(update, "Gagal menampilkan menu health")

    async def show_workout_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tampilkan menu workout"""
        try:
            keyboard = [
                [
                    InlineKeyboardButton("💪 Push Up", callback_data="workout_pushup"),
                    InlineKeyboardButton("⏱️ Plank", callback_data="workout_plank")
                ],
                [
                    InlineKeyboardButton("🦿 Squat", callback_data="workout_squat"),
                    InlineKeyboardButton("🏃 Running", callback_data="workout_running")
                ],
                [InlineKeyboardButton("🔙 Kembali", callback_data="health_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            text = (
                "*💪 WORKOUT MENU*\n\n"
                "*Pilih Workout:*\n"
                "• Push Up (100 cal/set)\n"
