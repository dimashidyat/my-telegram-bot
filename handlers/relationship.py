from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, date, timedelta
import logging
import json
import os
from config import GIRLFRIEND_PHONE, ANNIVERSARY_DATE

logger = logging.getLogger(__name__)

class RelationshipHandler:
    def __init__(self):
        self.data = {}
        self.girlfriend_phone = GIRLFRIEND_PHONE
        self.anniversary_date = ANNIVERSARY_DATE
        
        # Messages templates
        self.messages = {
            'morning': [
                "Selamat pagi sayangku 🌅\nSemoga harimu menyenangkan ya...\nI love you! 💖",
                "Good morning my love! 💝\nJangan lupa sarapan...\nThinking of you always 💭",
                "Pagi cintaku 💑\nSemoga Allah mudahkan semua urusanmu hari ini...\nLove you! 💕"
            ],
            'night': [
                "Selamat malam sayangku 🌙\nJaga kesehatan ya...\nSweet dreams! 💫",
                "Good night my love! 🌠\nMimpi indah ya sayang...\nI miss you! 💝",
                "Met bobo cintaku 😴\nIstirahat yang cukup...\nLove you so much! 💕"
            ],
            'random': [
                "Kamu tau ga kenapa aku sering senyum sendiri?\nSoalnya kamu selalu ada di pikiranku 💭",
                "Ya Allah... Terimakasih telah mengirimkan dia untukku 💝",
                "Bersamamu, setiap hari terasa spesial 💑"
            ]
        }
        
        # Load data
        self.load_data()

    def load_data(self):
        """Load relationship data"""
        try:
            if os.path.exists('data/relationship_data.json'):
                with open('data/relationship_data.json', 'r') as f:
                    self.data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading relationship data: {e}")

    def save_data(self):
        """Save relationship data"""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/relationship_data.json', 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving relationship data: {e}")

    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show relationship menu"""
        # Calculate relationship stats
        months = self.calculate_months()
        next_date = self.get_next_monthly()
        days_until = (next_date - date.today()).days
        milestone = self.get_next_milestone(months)

        keyboard = [
            [
                InlineKeyboardButton("💝 Love Notes", callback_data="relation_notes"),
                InlineKeyboardButton("📅 Dates", callback_data="relation_dates")
            ],
            [
                InlineKeyboardButton("💑 Quality Time", callback_data="relation_quality"),
                InlineKeyboardButton("🎁 Gift Ideas", callback_data="relation_gifts")
            ],
            [
                InlineKeyboardButton("📝 Journal", callback_data="relation_journal"),
                InlineKeyboardButton("⏰ Reminder", callback_data="relation_reminder")
            ],
            [InlineKeyboardButton("🔙 Menu Utama", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            "*💑 STATUS RELATIONSHIP*\n\n"
            f"• First Date: {self.anniversary_date.strftime('%d %B %Y')}\n"
            f"• Udah jalan: {months} bulan\n"
            f"• Monthly ke-{months+1}: {next_date.strftime('%d %B %Y')}\n"
            f"• Sisa: {days_until} hari lagi\n\n"
            f"*🎯 Next Milestone:*\n"
            f"• {milestone['desc']}\n"
            f"• {milestone['remaining']} bulan lagi\n\n"
            "_Semoga bisa terus bersama ya sayang_ 💕"
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

    def calculate_months(self) -> int:
        """Calculate months in relationship"""
        today = date.today()
        months = (today.year - self.anniversary_date.year) * 12
        months += today.month - self.anniversary_date.month
        
        if today.day < self.anniversary_date.day:
            months -= 1
            def get_next_monthly(self) -> date:
        """Get next monthly anniversary date"""
        today = date.today()
        next_date = today.replace(day=self.anniversary_date.day)
        
        if today.day >= self.anniversary_date.day:
            if next_date.month == 12:
                next_date = next_date.replace(year=next_date.year + 1, month=1)
            else:
                next_date = next_date.replace(month=next_date.month + 1)
        
        return next_date

    def get_next_milestone(self, current_months: int) -> dict:
        """Get next relationship milestone"""
        milestones = [
            {'months': 24, 'desc': '2 Tahun Anniversary 💑'},
            {'months': 30, 'desc': '2.5 Tahun Together 💕'},
            {'months': 36, 'desc': '3 Tahun Journey 💖'},
            {'months': 42, 'desc': '3.5 Tahun Strong 💝'},
            {'months': 48, 'desc': '4 Tahun of Love 💫'}
        ]
        
        for milestone in milestones:
            if current_months < milestone['months']:
                return {
                    'desc': milestone['desc'],
                    'remaining': milestone['months'] - current_months
                }
        
        return {
            'desc': 'Road to Halal 💍',
            'remaining': '???'
        }

    async def handle_love_notes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle love notes menu"""
        keyboard = [
            [
                InlineKeyboardButton("💝 Morning Love", callback_data="notes_morning"),
                InlineKeyboardButton("🌙 Night Love", callback_data="notes_night")
            ],
            [
                InlineKeyboardButton("💌 Sweet Message", callback_data="notes_sweet"),
                InlineKeyboardButton("✨ Custom Note", callback_data="notes_custom")
            ],
            [InlineKeyboardButton("🔙 Kembali", callback_data="relation_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            "*💌 LOVE NOTES*\n\n"
            "Pilih jenis pesan:\n\n"
            "1️⃣ Morning Love\n"
            "• Ucapan selamat pagi\n"
            "• Motivasi untuk dia\n\n"
            "2️⃣ Night Love\n"
            "• Ucapan selamat malam\n"
            "• Sweet dreams message\n\n"
            "3️⃣ Sweet Message\n"
            "• Random love notes\n"
            "• Kata-kata manis\n\n"
            "4️⃣ Custom Note\n"
            "• Bikin pesan sendiri\n"
            "• Format bebas\n\n"
            "_Tips: Kirim di waktu yang tepat!_ 💕"
        )

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_quality_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle quality time menu"""
        keyboard = [
            [
                InlineKeyboardButton("🎬 Movie Date", callback_data="quality_movie"),
                InlineKeyboardButton("🍽️ Dinner Date", callback_data="quality_dinner")
            ],
            [
                InlineKeyboardButton("🏃‍♂️ Active Date", callback_data="quality_active"),
                InlineKeyboardButton("🏡 Home Date", callback_data="quality_home")
            ],
            [
                InlineKeyboardButton("📅 Plan Custom", callback_data="quality_custom"),
                InlineKeyboardButton("💌 Invite Her", callback_data="quality_invite")
            ],
            [InlineKeyboardButton("🔙 Kembali", callback_data="relation_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            "*💑 QUALITY TIME IDEAS*\n\n"
            "*Budget Options:*\n"
            "1️⃣ Movie Date (50-100k)\n"
            "• Nonton bareng\n"
            "• Snack & drinks\n\n"
            "2️⃣ Dinner Date (150-200k)\n"
            "• Makan malam romantis\n"
            "• Cafe/resto kesukaan\n\n"
            "3️⃣ Active Date (0-50k)\n"
            "• Jalan/jogging bareng\n"
            "• Piknik di taman\n\n"
            "4️⃣ Home Date (50k)\n"
            "• Masak bareng\n"
            "• Movie marathon\n\n"
            "_Tips: Planning > Spending_ 💕"
        )

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_gift_ideas(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle gift ideas menu"""
        keyboard = [
            [
                InlineKeyboardButton("💝 Budget < 100k", callback_data="gift_budget"),
                InlineKeyboardButton("🎁 100k-500k", callback_data="gift_medium")
            ],
            [
                InlineKeyboardButton("✨ Special > 500k", callback_data="gift_special"),
                InlineKeyboardButton("💌 DIY Gifts", callback_data="gift_diy")
            ],
            [InlineKeyboardButton("🔙 Kembali", callback_data="relation_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            "*🎁 GIFT IDEAS*\n\n"
            "*Budget Options:*\n\n"
            "1️⃣ Budget (< 100k)\n"
            "• Handmade card/letter\n"
            "• Photo frame/album\n"
            "• Small plushies\n\n"
            "2️⃣ Medium (100-500k)\n"
            "• Parfum kesukaannya\n"
            "• Couple items\n"
            "• Accessories\n\n"
            "3️⃣ Special (> 500k)\n"
            "• Birthday surprise\n"
            "• Special dinner\n"
            "• Branded items\n\n"
            "4️⃣ DIY Gifts\n"
            "• Scrapbook memories\n"
            "• Handmade cookies\n"
            "• Custom playlist\n\n"
            "_Tips: Effort > Price_ 💝"
        )

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle reminders menu"""
        keyboard = [
            [
                InlineKeyboardButton("🌅 Morning Call", callback_data="remind_morning"),
                InlineKeyboardButton("🌙 Night Call", callback_data="remind_night")
            ],
            [
                InlineKeyboardButton("💊 Medicine", callback_data="remind_medicine"),
                InlineKeyboardButton("🍽️ Meals", callback_data="remind_meals")
            ],
            [
                InlineKeyboardButton("📅 Important Dates", callback_data="remind_dates"),
                InlineKeyboardButton("⚙️ Settings", callback_data="remind_settings")
            ],
            [InlineKeyboardButton("🔙 Kembali", callback_data="relation_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            "*⏰ REMINDER SETTINGS*\n\n"
            "*Current Reminders:*\n"
            "• Morning Call: 06:00\n"
            "• Night Call: 21:00\n"
            "• Meals: 3x sehari\n"
            "• Medicine: as needed\n\n"
            "*Important Dates:*\n"
            "• Monthly: 13\n"
            "• Birthday: 16 Sep\n"
            "• Anniversary: 13 Sep\n\n"
            "_Pilih untuk edit reminder_ ⚙️"
        )

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_error(self, update: Update, message: str):
        """Handle errors"""
        error_text = (
            f"❌ {message}\n\n"
            "Coba:\n"
            "1. Ketik /start\n"
            "2. Pilih menu Relationship lagi\n"
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
