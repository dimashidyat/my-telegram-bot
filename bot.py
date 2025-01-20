import os
import logging
import asyncio
from datetime import datetime, time, date
import random
from telegram.constants import ParseMode
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# States
(CHOOSING, TYPING_REPORT, TYPING_STUDY, TYPING_HEALTH,
 TYPING_SPIRITUAL, VIEWING_STATS) = range(6)

class LifeManagementBot:
    def __init__(self):
        # Bot credentials
        self.TOKEN = "7092522264:AAHsi2KM-8D8XcfIg09vptDyHiB28lRKQJY"
        self.CHAT_ID = "2031898002"
        
        # Personal data
        self.GIRLFRIEND_PHONE = "6281513607410"  
        self.MY_PHONE = "6281776633344"
        self.ANNIVERSARY_DATE = date(2021, 9, 13)
        
        # Storage
        self.reports = {}
        
        # Prayer times
        self.prayer_times = {
            'Subuh': time(4, 30),
            'Dzuhur': time(12, 0),
            'Ashar': time(15, 30),
            'Maghrib': time(18, 0),
            'Isya': time(19, 30)
        }

    async def setup_daily_reminders(self, application):
        """Setup all daily reminders."""
        # Morning message (5 AM)
        application.job_queue.run_daily(
            self.send_morning_message,
            time=time(5, 0),
            chat_id=self.CHAT_ID,
            name='morning_message'
        )
        
        # Prayer reminders
        for prayer, prayer_time in self.prayer_times.items():
            application.job_queue.run_daily(
                self.send_prayer_reminder,
                time=prayer_time,
                chat_id=self.CHAT_ID,
                name=f'prayer_{prayer.lower()}',
                data={'prayer': prayer}
            )
        
        # Monthly Anniversary reminder (00:00 on 13th)
        application.job_queue.run_daily(
            self.check_monthly_anniversary,
            time=time(0, 0),
            chat_id=self.CHAT_ID,
            name='monthly_anniversary'
        )
        
        # Anniversary check (00:00)
        application.job_queue.run_daily(
            self.check_anniversary,
            time=time(0, 0),
            chat_id=self.CHAT_ID,
            name='anniversary_check'
        )
        
        # Pempek report reminder (21:00)
        application.job_queue.run_daily(
            self.send_report_reminder,
            time=time(21, 0),
            chat_id=self.CHAT_ID,
            name='pempek_report'
        )
        
        # Study reminder (09:00)
        application.job_queue.run_daily(
            self.send_study_reminder,
            time=time(9, 0),
            chat_id=self.CHAT_ID,
            name='study_reminder'
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start command handler."""
        keyboard = [
            ['📝 Laporan Pempek', '📚 Study Log'],
            ['🕌 Spiritual', '💪 Health'],
            ['💕 Status Anniversary', '📊 Statistics'],
            ['⏰ Reminders', '❓ Help']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            'Assalamualaikum! 🌟\n\n'
            'Selamat datang di Bot Management.\n'
            'Pilih menu yang kamu butuhkan:',
            reply_markup=reply_markup
        )
        return CHOOSING

    async def pempek_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle pempek report menu."""
        template = """
*Format Laporan Pempek*

1. *Pengeluaran*
Format: Item: jumlah
Contoh:
Air: 4000
Gas: 22000

2. *Sisa*
a. Kecil: jumlah (x2.500)
b. Gede: jumlah (x12.000)

3. *Setoran*
QRIS: jumlah
Cash: jumlah

4. *Sisa Plastik*
a. 1/4: Br=jumlah, Bs=jumlah
b. 1/2: Br=jumlah, Bs=jumlah
c. 1: Br=jumlah, Bs=jumlah
d. Kantong: Br=jumlah, Bs=jumlah

5. *Status Minyak*
(abis/masih)

Ketik laporan sesuai format di atas.
"""
        await update.message.reply_text(
            template,
            parse_mode=ParseMode.MARKDOWN
        )
        return TYPING_REPORT

    async def handle_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle pempek report submission."""
        report_text = update.message.text
        date_str = datetime.now().strftime('%Y-%m-%d')
        self.reports[date_str] = report_text
        
        await update.message.reply_text(
            "✅ Laporan berhasil disimpan!\n\n"
            "Ketik /start untuk kembali ke menu utama."
        )
        return ConversationHandler.END

    async def send_morning_message(self, context: ContextTypes.DEFAULT_TYPE):
        """Send morning love message."""
        messages = [
            "Pagi sayang 💕\nSemoga hari ini penuh berkah ya.\nJangan lupa sarapan!\n\nLove you 😘",
            "Good morning my love 💝\nSelalu semangat ya hari ini.\nAku selalu mendukungmu!\n\nI love you 💑",
            "Selamat pagi cintaku 💖\nSemoga harimu menyenangkan.\nJaga kesehatan ya!\n\nLove you always 🥰"
        ]
        message = random.choice(messages)
        keyboard = [
            [InlineKeyboardButton("💌 Balas Pesan", url=f"https://wa.me/{self.GIRLFRIEND_PHONE}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await context.bot.send_message(
                chat_id=self.CHAT_ID,
                text=message,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error sending morning message: {e}")

    async def send_prayer_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        """Send prayer reminder."""
        prayer = context.job.data['prayer']
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=f"🕌 Waktu {prayer} telah tiba!\n\nJangan lupa sholat ya..."
        )

    async def check_monthly_anniversary(self, context: ContextTypes.DEFAULT_TYPE):
        """Check and send monthly anniversary reminder."""
        today = date.today()
        if today.day == 13:  # Cek setiap tanggal 13
            months = self.calculate_months()
            message = f"""
🎉 *Monthly Anniversary ke-{months}!* 🎉

Alhamdulillah sudah {months} bulan kita jalani bersama.
Semoga kita bisa terus bersama sampai halal ya sayang.

I love you so much! 💑
            """
            keyboard = [
                [InlineKeyboardButton("💝 Chat Sayang", url=f"https://wa.me/{self.GIRLFRIEND_PHONE}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await context.bot.send_message(
                    chat_id=self.CHAT_ID,
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Error sending monthly anniversary message: {e}")

    async def check_anniversary(self, context: ContextTypes.DEFAULT_TYPE):
        """Check and send annual anniversary reminder."""
        today = date.today()
        if today.month == self.ANNIVERSARY_DATE.month and today.day == self.ANNIVERSARY_DATE.day:
            years = today.year - self.ANNIVERSARY_DATE.year
            message = f"""
🎉 *Happy {years} Year Anniversary!* 🎉

Alhamdulillah sudah {years} tahun kita jalani bersama.
Semoga kita bisa terus bersama sampai halal ya sayang.

I love you forever! 💑
            """
            keyboard = [
                [InlineKeyboardButton("💝 Chat Sayang", url=f"https://wa.me/{self.GIRLFRIEND_PHONE}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await context.bot.send_message(
                    chat_id=self.CHAT_ID,
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Error sending anniversary message: {e}")

    async def send_report_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        """Send reminder for pempek report."""
        await context.bot.send_message(
            chat_id=self.CHAT_ID,
            text="🔔 Reminder!\n\nJangan lupa buat laporan pempek hari ini ya!"
        )

    async def send_study_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        """Send reminder for studying."""
        await context.bot.send_message(
            chat_id=self.CHAT_ID,
            text="📚 Study Time!\n\nWaktunya belajar dan persiapan BULOG!"
        )

    def calculate_months(self) -> int:
        """Calculate months since anniversary date."""
        today = date.today()
        months = (today.year - self.ANNIVERSARY_DATE.year) * 12 + (today.month - self.ANNIVERSARY_DATE.month)
        if today.day < self.ANNIVERSARY_DATE.day:
            months -= 1
        return months

    async def show_anniversary_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show anniversary status."""
        months = self.calculate_months()
        next_date = date.today().replace(day=13)
        if date.today().day > 13:
            if next_date.month == 12:
                next_date = next_date.replace(year=next_date.year + 1, month=1)
            else:
                next_date = next_date.replace(month=next_date.month + 1)
        
        days_until = (next_date - date.today()).days
        
        message = (
            f"💑 *Status Anniversary*\n\n"
            f"• Mulai pacaran: 13 September 2021\n"
            f"• Sudah berjalan: {months} bulan\n"
            f"• Anniversary berikutnya: {next_date.strftime('%d %B %Y')}\n"
            f"• Sisa hari: {days_until} hari lagi\n\n"
            f"_Semoga kita bisa terus bersama ya sayang_ 💕"
        )
        
        keyboard = [
            [InlineKeyboardButton("💝 Chat Sayang", url=f"https://wa.me/{self.GIRLFRIEND_PHONE}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        return CHOOSING

    def run(self):
        """Run the bot."""
        try:
            # Create application
            application = ApplicationBuilder().token(self.TOKEN).build()

            # Setup reminders
            asyncio.get_event_loop().run_until_complete(
                self.setup_daily_reminders(application)
            )

            # Add conversation handler
            conv_handler = ConversationHandler(
                entry_points=[CommandHandler('start', self.start)],
                states={
                    CHOOSING: [
                        MessageHandler(filters.Regex('^📝 Laporan Pempek$'), self.pempek_menu),
                        MessageHandler(filters.Regex('^💕 Status Anniversary$'), self.show_anniversary_status),
                    ],
                    TYPING_REPORT: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_report)
                    ],
                },
                fallbacks=[CommandHandler('start', self.start)]
            )

            application.add_handler(conv_handler)
            
            # Start bot
            print("Bot started successfully! 🚀")
            application.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            logger.error(f"Error running bot: {e}")
            raise e

if __name__ == '__main__':
    bot = LifeManagementBot()
    bot.run()
