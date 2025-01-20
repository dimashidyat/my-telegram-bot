from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
import logging
from config import CHANNELS, STUDY_MATERIALS

logger = logging.getLogger(__name__)

class StudyHandler:
    def __init__(self):
        self.data = {}
        self.session = {}
        self.targets = {
            'TWK': {'target': 20, 'done': 0},
            'TIU': {'target': 15, 'done': 0},
            'TKP': {'target': 10, 'done': 0}
        }

    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tampilkan menu study"""
        try:
            user_id = update.effective_user.id
            if user_id not in self.data:
                self.data[user_id] = {
                    'TWK': 0,
                    'TIU': 0,
                    'TKP': 0,
                    'study_time': 0,
                    'last_study': None
                }

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
                    InlineKeyboardButton("📱 Join Channel BULOG", url=f"https://t.me/{CHANNELS['bumn']}"),
                    InlineKeyboardButton("🔙 Menu Utama", callback_data="back_main")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            today_data = self.data[user_id]
            
            text = (
                "*📚 MENU BELAJAR BULOG*\n\n"
                "*Progress Hari Ini:*\n"
                f"• TWK: {today_data['TWK']}/{self.targets['TWK']['target']} soal\n"
                f"• TIU: {today_data['TIU']}/{self.targets['TIU']['target']} soal\n"
                f"• TKP: {today_data['TKP']}/{self.targets['TKP']['target']} soal\n\n"
                f"⏱️ Total waktu belajar: {today_data['study_time']} menit\n\n"
                "*Tips:*\n"
                "• TWK: Fokus ke Pancasila & UUD\n"
                "• TIU: Latihan logika tiap hari\n"
                "• TKP: Pahami karakteristik PNS"
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
            await self.handle_error(update, "Gagal menampilkan menu study")

    async def handle_timer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle study timer"""
        try:
            user_id = update.effective_user.id
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
                "Pilih durasi belajar:\n\n"
                "*Rekomendasi:*\n"
                "• 25 min = 1 sesi Pomodoro\n"
                "• 45 min = Deep focus\n"
                "• Custom = Set sendiri\n\n"
                "Tips: Break 5 menit tiap sesi!"
            )

            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error in handle_timer: {e}")
            await self.handle_error(update, "Gagal mengatur timer")

    async def start_timer(self, update: Update, duration: int):
        """Start study timer"""
        try:
            user_id = update.effective_user.id
            now = datetime.now()
            
            self.session[user_id] = {
                'start_time': now,
                'duration': duration,
                'end_time': now + timedelta(minutes=duration)
            }

            # Set timer job
            context.job_queue.run_once(
                self.timer_finished,
                duration * 60,
                context={'user_id': user_id, 'chat_id': update.effective_chat.id}
            )

            keyboard = [[InlineKeyboardButton("⏹️ Stop Timer", callback_data="timer_stop")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.callback_query.edit_message_text(
                f"⏱️ Timer dimulai: {duration} menit\n"
                f"Selesai pada: {self.session[user_id]['end_time'].strftime('%H:%M')}\n\n"
                "Semangat belajarnya! 💪",
                reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error starting timer: {e}")
            await self.handle_error(update, "Gagal memulai timer")

    async def timer_finished(self, context):
        """Handle timer finished"""
        try:
            job = context.job
            user_id = job.context['user_id']
            chat_id = job.context['chat_id']

            if user_id in self.session:
                duration = self.session[user_id]['duration']
                self.data[user_id]['study_time'] += duration
                del self.session[user_id]

                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"⏰ *Timer Selesai!*\n\n"
                         f"✅ Sudah belajar {duration} menit\n"
                         f"🎯 Total hari ini: {self.data[user_id]['study_time']} menit\n\n"
                         "Mau lanjut belajar?",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("⏱️ Timer Baru", callback_data="study_timer"),
                        InlineKeyboardButton("📊 Lihat Progress", callback_data="study_progress")
                    ]])
                )

        except Exception as e:
            logger.error(f"Error in timer_finished: {e}")

    async def handle_error(self, update: Update, message: str):
        """Handle errors"""
        error_text = (
            f"❌ {message}\n\n"
            "Coba:\n"
            "1. Ketik /start\n"
            "2. Pilih menu Study BULOG lagi"
        )
        
        if update.callback_query:
            await update.callback_query.message.reply_text(error_text)
        else:
            await update.message.reply_text(error_text)
