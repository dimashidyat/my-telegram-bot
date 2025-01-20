from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
import logging
import json
import os
from config import STUDY_MATERIALS, CHANNELS

logger = logging.getLogger(__name__)

class StudyHandler:
    def __init__(self):
        self.data = {}
        self.active_timers = {}
        self.targets = {
            'TWK': {'target': 20, 'done': 0},
            'TIU': {'target': 15, 'done': 0},
            'TKP': {'target': 10, 'done': 0}
        }
        
        # Load existing data
        self.load_data()

    def load_data(self):
        """Load study data from file"""
        try:
            if os.path.exists('data/study_data.json'):
                with open('data/study_data.json', 'r') as f:
                    self.data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading study data: {e}")

    def save_data(self):
        """Save study data to file"""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/study_data.json', 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving study data: {e}")

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
            [
                InlineKeyboardButton("📱 Join Channel BULOG", url=f"https://t.me/{CHANNELS['bumn']}"),
                InlineKeyboardButton("🔙 Menu Utama", callback_data="back_main")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Get user stats
        user_id = str(update.effective_user.id)
        stats = self.get_user_stats(user_id)
        
        text = (
            "*📚 MENU BELAJAR BULOG*\n\n"
            "*Progress Hari Ini:*\n"
            f"• TWK: {stats['TWK']}/{self.targets['TWK']['target']} soal\n"
            f"• TIU: {stats['TIU']}/{self.targets['TIU']['target']} soal\n"
            f"• TKP: {stats['TKP']}/{self.targets['TKP']['target']} soal\n\n"
            f"⏱️ Total waktu: {stats['study_time']} menit\n"
            f"🔥 Streak: {stats['streak']} hari\n\n"
            "*Tips:*\n"
            "• Focus mode = 25 menit\n"
            "• Break = 5 menit\n"
            "• Join channel untuk soal harian"
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

    async def handle_timer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle study timer"""
        keyboard = [
            [
                InlineKeyboardButton("⏰ 25 min", callback_data="timer_25"),
                InlineKeyboardButton("⏰ 45 min", callback_data="timer_45")
            ],
            [InlineKeyboardButton("⏰ Custom", callback_data="timer_custom")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="study_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            "*⏱️ STUDY TIMER*\n\n"
            "*Pilih durasi:*\n"
            "• 25 min = 1 sesi Pomodoro\n"
            "• 45 min = Deep focus\n"
            "• Custom = Set sendiri\n\n"
            "_Tips: Break 5 menit tiap sesi!_"
        )

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def start_timer(self, update: Update, context: ContextTypes.DEFAULT_TYPE, duration: int):
        """Start a study timer"""
        try:
            user_id = str(update.effective_user.id)
            now = datetime.now()
            end_time = now + timedelta(minutes=duration)
            
            # Save timer data
            self.active_timers[user_id] = {
                'start_time': now,
                'duration': duration,
                'end_time': end_time
            }

            # Create timer job
            context.job_queue.run_once(
                self.timer_finished,
                duration * 60,
                chat_id=update.effective_chat.id,
                user_id=user_id
            )

            keyboard = [[InlineKeyboardButton("⏹️ Stop Timer", callback_data="timer_stop")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.callback_query.edit_message_text(
                f"⏱️ Timer dimulai: {duration} menit\n"
                f"Selesai pada: {end_time.strftime('%H:%M')}\n\n"
                "Semangat belajarnya! 💪",
                reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error starting timer: {e}")
            await self.handle_error(update, "Gagal memulai timer")

    async def timer_finished(self, context):
        """Handle timer completion"""
        job = context.job
        user_id = job.user_id
        chat_id = job.chat_id

        try:
            if user_id in self.active_timers:
                duration = self.active_timers[user_id]['duration']
                
                # Update study time
                if user_id not in self.data:
                    self.data[user_id] = {'study_time': 0}
                self.data[user_id]['study_time'] += duration
                
                # Save data
                self.save_data()
                
                # Clean up timer
                del self.active_timers[user_id]

                keyboard = [
                    [
                        InlineKeyboardButton("⏱️ Timer Baru", callback_data="study_timer"),
                        InlineKeyboardButton("📊 Progress", callback_data="study_progress")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await context.bot.send_message(
                    chat_id=chat_id,
                    text=(
                        "⏰ *Timer Selesai!*\n\n"
                        f"✅ Sudah belajar {duration} menit\n"
                        "Mau lanjut atau cek progress?"
                    ),
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )

        except Exception as e:
            logger.error(f"Error in timer_finished: {e}")

    def get_user_stats(self, user_id: str) -> dict:
        """Get user's study statistics"""
        default_stats = {
            'TWK': 0,
            'TIU': 0,
            'TKP': 0,
            'study_time': 0,
            'streak': 0
        }
        
        return self.data.get(str(user_id), default_stats)

    async def handle_error(self, update: Update, message: str):
        """Handle errors"""
        error_text = (
            f"❌ {message}\n\n"
            "Coba:\n"
            "1. Ketik /start\n"
            "2. Pilih menu Study lagi\n"
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
