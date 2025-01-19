from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
import pytz
import random
import json
import logging
import requests
from io import BytesIO
import matplotlib.pyplot as plt

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Token
TOKEN = os.environ.get(7092522264:AAHsi2KM-8D8XcfIg09vptDyHiB28lRKQJY)

# Constants untuk tracking progress
WORKOUT = 0
STUDY = 1
WORK = 2

# Detail jadwal lengkap (ini jadwal lo yang super detail)
COMPLETE_SCHEDULE = {
    # Pagi - The Morning Grind
    "04:45": {
        "activity": "🌅 BANGUN PAGI CHAMPIONS!",
        "details": [
            "1. Langsung duduk (no debat)",
            "2. Minum air putih segelas",
            "3. Cuci muka pake air dingin",
            "4. Wudhu",
            "5. DILARANG BALIK TIDUR!"
        ]
    },
    "05:00": {
        "activity": "🕌 SPIRITUAL TIME",
        "details": [
            "1. Sholat Subuh",
            "2. Dzikir ringkas",
            "3. Afirmasi pagi:",
            "   - 'Hari ini gue lebih baik'",
            "   - 'Progress > Perfection'",
            "   - 'Small wins count!'"
        ]
    },
    "05:15": {
        "activity": "💪 WORKOUT TIME",
        "details": [
            "Level 1 (Minggu 1-2):",
            "- Push up 5x (nambah 2/minggu)",
            "- Plank 20 detik (nambah 5 detik/minggu)",
            "- Squat 10x (nambah 5/minggu)",
            "- Jumping jack 20x"
        ]
    },
    "05:30": {
        "activity": "🚿 OPERASI GANTENG",
        "details": [
            "1. Mandi:",
            "   - Sabun wangi",
            "   - Sikat gigi bersih",
            "   - Facial wash",
            "2. Grooming:",
            "   - Moisturizer",
            "   - Deodoran",
            "   - Sisir rambut",
            "   - Parfum (dikit aja)"
        ]
    },

    # Maxim Time
    "06:00": {
        "activity": "🏍️ MAXIM TIME",
        "details": [
            "Strategy per jam:",
            "06:00-07:30: Daerah perumahan",
            "07:30-09:00: Area sekolah/kantor",
            "09:00-10:00: Kawasan bisnis",
            "Target: 50k minimum!"
        ]
    },

    # Study Time
    "10:00": {
        "activity": "📚 BELAJAR BULOG",
        "details": [
            "Setup:",
            "1. Clear meja",
            "2. HP silent & jauh",
            "3. Air putih ready",
            "4. Pomodoro method:",
            "   - 25 menit fokus",
            "   - 5 menit break",
            "   - Repeat 4x"
        ]
    },

    # Business Time
    "14:00": {
        "activity": "💼 PEMPEK TIME",
        "details": [
            "Prime hours:",
            "16:00-18:00: Shift pabrik pulang",
            "18:00-19:30: Office hours",
            "19:30-21:00: Dinner time",
            "21:00-23:00: Last orders"
        ]
    },
}

# Quotes motivasi yang lebih lengkap
MOTIVATION_QUOTES = [
    "🔥 Bangun pagi itu susah, tapi jadi miskin lebih susah!",
    "💪 Lo nggak bisa download otot & upload lemak.",
    "✨ Bokap nyokap nggak muda terus, buruan sukses!",
    "⭐ Yang konsisten biasa > Yang sempurna kadang-kadang.",
    "🌟 Pacar bisa pergi, skill stays forever.",
    "🎯 Success is built in the morning!",
    "⚡ Mimpi lo gak akan terwujud dengan tidur terus.",
    "🌅 Setiap subuh adalah kesempatan baru buat jadi lebih baik.",
    "💡 Lo lebih kuat dari yang lo kira.",
    "🚀 BULOG is waiting for you, champion!"
]

# Emergency protocols
EMERGENCY_PROTOCOLS = {
    "telat_bangun": [
        "1. NO PANIC!",
        "2. Skip workout",
        "3. Mandi kilat (5 menit)",
        "4. Grooming minimal",
        "5. GO GO GO!"
    ],
    "mental_down": [
        "1. Sholat dulu",
        "2. Deep breath 10x",
        "3. Minum air putih",
        "4. Keluar kamar",
        "5. Call support system"
    ],
    "pmo_triggered": [
        "1. Wudhu/mandi",
        "2. Push up sampe capek",
        "3. Keluar kamar",
        "4. Jalan-jalan",
        "5. Productive activity"
    ]
}

# Progress tracking
user_progress = {}

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    keyboard = [
        [
            InlineKeyboardButton("📅 Jadwal", callback_data='schedule'),
            InlineKeyboardButton("💪 Progress", callback_data='progress')
        ],
        [
            InlineKeyboardButton("🆘 Emergency", callback_data='emergency'),
            InlineKeyboardButton("💡 Tips", callback_data='tips')
        ],
        [
            InlineKeyboardButton("📊 Statistik", callback_data='stats'),
            InlineKeyboardButton("🎯 Target", callback_data='goals')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = (
        f"Assalamualaikum {user.first_name}! 👋\n\n"
        "Gue Dimas Bot, asisten pribadi yang bakal bantu lo jadi versi terbaik dari diri lo! 🚀\n\n"
        "Fitur-fitur gue:\n"
        "📅 /jadwal - Full schedule hari ini\n"
        "⏰ /reminder - Nyalain reminder\n"
        "🔕 /mute - Matiin reminder\n"
        "💪 /progress - Track progress lo\n"
        "🆘 /sos - Quick help buat emergency\n"
        "📚 /bumn - Soal BUMN hari ini\n"
        "💡 /tips - Random productivity tips\n"
        "🎯 /target - Set & track target lo\n\n"
        "Siap temani lo jadi sukses! 💪"
    )
    
    update.message.reply_text(welcome_message, reply_markup=reply_markup)

def show_progress(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    
    if user_id not in user_progress:
        user_progress[user_id] = {
            "workout": 0,
            "study": 0,
            "work": 0,
            "streak": 0
        }
    
    progress = user_progress[user_id]
    
    # Bikin grafik progress
    labels = ['Workout', 'Study', 'Work']
    values = [progress['workout'], progress['study'], progress['work']]
    
    plt.figure(figsize=(10, 5))
    plt.bar(labels, values)
    plt.title('Your Progress This Week')
    
    # Save plot ke buffer
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Kirim grafik ke user
    update.message.reply_photo(
        photo=buf,
        caption=f"📊 PROGRESS REPORT:\n\n"
                f"💪 Workout streak: {progress['workout']} hari\n"
                f"📚 Study time: {progress['study']} jam\n"
                f"💼 Work performance: {progress['work']}%\n"
                f"🔥 Current streak: {progress['streak']} hari\n\n"
                f"Keep going champion! 🚀"
    )

def emergency_help(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("😴 Telat Bangun", callback_data='telat_bangun'),
            InlineKeyboardButton("😔 Mental Down", callback_data='mental_down')
        ],
        [
            InlineKeyboardButton("😣 PMO Triggered", callback_data='pmo_triggered'),
            InlineKeyboardButton("😫 Stress", callback_data='stress')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        "🆘 EMERGENCY HELP!\n\n"
        "Pilih kondisi emergency lo:",
        reply_markup=reply_markup
    )

def bumn_soal(update: Update, context: CallbackContext) -> None:
    # Forward soal dari channel BUMN
    try:
        # Ini bisa diganti dengan logic buat ambil soal dari channel @latihansoalbumn2025
        update.message.reply_text(
            "📚 SOAL BUMN HARI INI:\n\n"
            "[Soal dari channel akan muncul di sini]\n\n"
            "Semangat berlatih! 💪"
        )
    except Exception as e:
        logger.error(f"Error in bumn_soal: {str(e)}")
        update.message.reply_text("Maaf, ada error. Coba lagi nanti ya!")

def handle_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    if query.data in EMERGENCY_PROTOCOLS:
        protocol = "\n".join(EMERGENCY_PROTOCOLS[query.data])
        query.edit_message_text(
            f"🆘 EMERGENCY PROTOCOL: {query.data.upper()}\n\n{protocol}"
        )
    elif query.data == 'progress':
        show_progress(update, context)
    # Handle other callbacks...

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("jadwal", show_schedule))
    dispatcher.add_handler(CommandHandler("reminder", set_reminders))
    dispatcher.add_handler(CommandHandler("mute", mute_reminders))
    dispatcher.add_handler(CommandHandler("progress", show_progress))
    dispatcher.add_handler(CommandHandler("sos", emergency_help))
    dispatcher.add_handler(CommandHandler("bumn", bumn_soal))
    
    dispatcher.add_handler(CallbackQueryHandler(handle_callback))
    
    # Start the Bot
    updater.start_polling()
    updater.id
if __name__ == '__main__':
    main(
