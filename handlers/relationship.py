from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, date, timedelta
import logging
import random
import json

logger = logging.getLogger(__name__)

class RelationshipHandler:
    def __init__(self):
        self.couple_data = {}
        self.anniversary_date = date(2021, 9, 13)
        self.girlfriend_phone = "6281513607410"
        
        # Collection of romantic messages
        self.love_messages = {
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

        # Romantic gift ideas
        self.gift_ideas = {
            'budget': [
                "Surat cinta handmade 💌",
                "Playlist lagu favorit kita 🎵",
                "Photo collage memories kita 📸"
            ],
            'medium': [
                "Flower bouquet favorit dia 💐",
                "Parfum kesukaannya 🌸",
                "Boneka couple yang lucu 🧸"
            ],
            'special': [
                "Surprise birthday dinner 🎂",
                "Weekend getaway ke tempat favorit 🏖️",
                "Handmade scrapbook memories 📒"
            ]
        }

        # Date ideas
        self.date_ideas = {
            'simple': [
                {
                    'name': "Movie Night 🎬",
                    'desc': "Nonton film favorit bareng, sambil makan snack",
                    'budget': "50-100k"
                },
                {
                    'name': "Picnic Sore 🧺",
                    'desc': "Bawa bekal, duduk sambil ngobrol di taman",
                    'budget': "50-100k"
                }
            ],
            'medium': [
                {
                    'name': "Dinner Date 🍽️",
                    'desc': "Makan malam romantis di resto kesukaan",
                    'budget': "200-300k"
                },
                {
                    'name': "Adventure Date 🎯",
                    'desc': "Main ke timezone atau tempat seru lainnya",
                    'budget': "200-300k"
                }
            ],
            'special': [
                {
                    'name': "Staycation Weekend 🏨",
                    'desc': "Quality time berdua di hotel/villa",
                    'budget': "500k+"
                }
            ]
        }

    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tampilkan menu relationship yang romantis"""
        try:
            months = self.calculate_months()
            next_date = self.get_next_monthly()
            days_until = (next_date - date.today()).days

            keyboard = [
                [
                    InlineKeyboardButton("💝 Love Notes", callback_data="love_notes"),
                    InlineKeyboardButton("🎁 Gift Ideas", callback_data="gift_ideas")
                ],
                [
                    InlineKeyboardButton("📅 Date Planner", callback_data="date_planner"),
                    InlineKeyboardButton("💌 Send Message", callback_data="send_message")
                ],
                [
                    InlineKeyboardButton("🌟 Memories", callback_data="memories"),
                    InlineKeyboardButton("💑 About Us", callback_data="about_us")
                ],
                [InlineKeyboardButton("🔙 Menu Utama", callback_data="back_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Get relationship milestone
            milestone = self.get_next_milestone(months)
            
            text = (
                "*💑 STATUS RELATIONSHIP*\n\n"
                f"• First Date: 13 September 2021\n"
                f"• Udah jalan: {months} bulan\n"
                f"• Monthly ke-{months+1}: {next_date.strftime('%d %B %Y')}\n"
                f"• Sisa: {days_until} hari lagi\n\n"
                f"*🎯 Next Milestone:*\n"
                f"• {milestone['desc']}\n"
                f"• {milestone['remaining']} bulan lagi\n\n"
                "_Semoga kita bisa terus bersama ya sayang_ 💕"
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
            logger.error(f"Error showing menu: {e}")
            await self.handle_error(update, "Ada masalah teknis sayang...")

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

    async def show_love_notes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tampilkan love notes templates"""
        try:
            keyboard = [
                [
                    InlineKeyboardButton("💝 Morning Love", callback_data="note_morning"),
                    InlineKeyboardButton("🌙 Night Love", callback_data="note_night")
                ],
                [
                    InlineKeyboardButton("💌 Random Sweet", callback_data="note_random"),
                    InlineKeyboardButton("✨ Custom Note", callback_data="note_custom")
                ],
                [InlineKeyboardButton("🔙 Kembali", callback_data="relationship_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            text = (
                "*💌 LOVE NOTES*\n\n"
                "Pilih jenis pesan cinta:\n\n"
                "• Morning = Ucapan selamat pagi\n"
                "• Night = Ucapan selamat malam\n"
                "• Random = Random sweet messages\n"
                "• Custom = Bikin pesan sendiri\n\n"
                "_Tips: Kirim pesan di waktu yang tepat ya!_ 💕"
            )

            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error showing love notes: {e}")
            await self.handle_error(update, "Gagal menampilkan love notes")

    async def send_love_note(self, note_type: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Kirim love note ke WhatsApp"""
        try:
            message = random.choice(self.love_messages[note_type])
            wa_link = f"https://wa.me/{self.girlfriend_phone}?text={message}"

            keyboard = [
                [InlineKeyboardButton("💌 Kirim via WA", url=wa_link)],
                [InlineKeyboardButton("🔄 Ganti Pesan", callback_data=f"note_{note_type}")],
                [InlineKeyboardButton("🔙 Kembali", callback_data="love_notes")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            text = (
                "*💌 PREVIEW MESSAGE*\n\n"
                f"{message}\n\n"
                "_Klik tombol di bawah untuk kirim_ 💕"
            )

            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error sending love note: {e}")
            await self.handle_error(update, "Gagal mengirim pesan")

    async def show_date_planner(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tampilkan date planner"""
        try:
            keyboard = [
                [
                    InlineKeyboardButton("💝 Simple Date", callback_data="date_simple"),
                    InlineKeyboardButton("✨ Special Date", callback_data="date_special")
                ],
                [
                    InlineKeyboardButton("📅 Plan Custom", callback_data="date_custom"),
                    InlineKeyboardButton("💌 Remind Her", callback_data="date_remind")
                ],
                [InlineKeyboardButton("🔙 Kembali", callback_data="relationship_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Get random date idea
            all_ideas = (
                self.date_ideas['simple'] + 
                self.date_ideas['medium'] + 
                self.date_ideas['special']
            )
            suggestion = random.choice(all_ideas)

            text = (
                "*📅 DATE PLANNER*\n\n"
                "*Rekomendasi Date:*\n"
                f"• {suggestion['name']}\n"
                f"• {suggestion['desc']}\n"
                f"• Budget: {suggestion['budget']}\n\n"
                "*Pilih opsi di bawah untuk:*\n"
                "• Lihat ide date simpel\n"
                "• Rencana date spesial\n"
                "• Bikin plan custom\n"
                "• Ingetin dia untuk date\n\n"
                "_Tips: Sesuaikan dengan waktu & budget_ 💕"
            )

            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error showing date planner: {e}")
            await self.handle_error(update, "Gagal menampilkan date planner")

    def calculate_months(self) -> int:
        """Hitung berapa bulan sudah pacaran"""
        today = date.today()
        months = (today.year - self.anniversary_date.year) * 12
        months += today.month - self.anniversary_date.month
        
        if today.day < self.anniversary_date.day:
            months -= 1
            
        return months

    def get_next_monthly(self) -> date:
        """Get tanggal monthly anniversary berikutnya"""
        today = date.today()
        next_date = today.replace(day=13)
        
        if today.day >= 13:
            if next_date.month == 12:
                next_date = next_date.replace(year=next_date.year + 1, month=1)
            else:
                next_date = next_date.replace(month=next_date.month + 1)
                
        return next_date

    async def handle_error(self, update: Update, message: str):
        """Handle errors dengan cara yang sweet"""
        error_text = (
            f"❤️ {message}\n\n"
            "Coba:\n"
            "1. Mulai dari /start\n"
            "2. Pilih menu Status Pacaran lagi\n"
            "3. Atau chat langsung aja ke dia 💝"
        )
        
        if update.callback_query:
            await update.callback_query.message.reply_text(error_text)
        else:
            await update.message.reply_text(error_text)

    def save_data(self):
        """Save relationship data"""
        try:
            with open('relationship_data.json', 'w') as f:
                json.dump(self.couple_data, f)
        except Exception as e:
            logger.error(f"Error saving data: {e}")

    def load_data(self):
        """Load relationship data"""
        try:
            with open('relationship_data.json', 'r') as f:
                self.couple_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.couple_data = {}
