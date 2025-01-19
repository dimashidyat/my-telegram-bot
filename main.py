import os
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
import schedule
import time
import threading
import json
import random

# Masukkan API Token bot lo
TOKEN = "7092522264:AAHsi2KM-8D8XcfIg09vptDyHiB28lRKQJY"
CHAT_ID = "2031898002"
DATA_FILE = "user_data.json"

# Inisialisasi data tracking
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

# Fungsi untuk baca data JSON
def read_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Fungsi untuk tulis data JSON
def write_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# Reminder otomatis
def send_reminder(bot, text):
    bot.send_message(chat_id=CHAT_ID, text=text)

def scheduler(bot):
    schedule.every().day.at("04:45").do(send_reminder, bot=bot, text="Bangun bro, waktunya sholat Subuh!")
    schedule.every().day.at("05:15").do(send_reminder, bot=bot, text="Olahraga dulu biar otot jadi!")
    schedule.every().day.at("10:00").do(send_reminder, bot=bot, text="Belajar CPNS 2 jam, fokus ya!")
    schedule.every().day.at("21:00").do(send_reminder, bot=bot, text="Evaluasi hari ini, lo udah keren bro!")
    schedule.every().day.at("22:00").do(send_reminder, bot=bot, text="Jangan lupa catat progress harian lo!")

    while True:
        schedule.run_pending()
        time.sleep(1)

# Fungsi untuk log otomatis
def auto_log(update, context, category, prompt):
    data = read_data()
    user_id = str(update.effective_user.id)
    if user_id not in data:
        data[user_id] = {"log": {}}
    if category not in data[user_id]["log"]:
        data[user_id]["log"][category] = []
    
    # Simpan log
    data[user_id]["log"][category].append(prompt)
    write_data(data)
    update.message.reply_text(f"Log otomatis untuk {category}: {prompt} berhasil disimpan.")

# Fungsi Command /start
def start(update, context):
    update.message.reply_text(
        "Halo bro! Gue bot lo. Siap bantu lo jadi lebih produktif. Ketik /menu buat lihat fitur."
    )

# Fungsi Command /menu
def menu(update, context):
    keyboard = [
        [InlineKeyboardButton("📋 Log Aktivitas", callback_data="log_menu"),
         InlineKeyboardButton("📚 Study Hub", callback_data="study_hub")],
        [InlineKeyboardButton("💰 Finance Tracker", callback_data="finance_menu"),
         InlineKeyboardButton("📊 Statistik", callback_data="stats_menu")],
        [InlineKeyboardButton("📝 Reminder", callback_data="reminder_menu"),
         InlineKeyboardButton("🔥 Motivasi", callback_data="motivasi")]
    ]

    update.message.reply_text(
        "Pilih menu:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Fungsi Latihan Soal Otomatis
def soal_otomatis(update, context):
    soal_list = [
        "Apa kepanjangan BUMN?",
        "Siapa Presiden pertama Indonesia?",
        "2 + 2 x 2 = ?"
    ]
    soal = random.choice(soal_list)
    update.message.reply_text(f"Latihan Soal: {soal}")

# Fungsi Timer Belajar
def start_timer(update, context):
    update.message.reply_text("Pomodoro Timer dimulai: 25 menit fokus.")
    time.sleep(25 * 60)  # 25 menit
    update.message.reply_text("Waktu fokus selesai. Istirahat 5 menit!")
    time.sleep(5 * 60)  # 5 menit
    update.message.reply_text("Istirahat selesai. Siap fokus lagi!")

# Fungsi Statistik Sederhana
def stats(update, context):
    data = read_data()
    user_id = str(update.effective_user.id)
    if user_id not in data:
        update.message.reply_text("Belum ada data untuk statistik.")
        return
    
    log = data[user_id]["log"]
    stats_text = "📊 Statistik Harian:\n"
    for category, entries in log.items():
        stats_text += f"- {category.capitalize()}: {len(entries)} kali\n"
    
    update.message.reply_text(stats_text)

# Main function
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command Handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("menu", menu))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("soal", soal_otomatis))
    dp.add_handler(CommandHandler("timer", start_timer))

    # Scheduler buat reminder
    threading.Thread(target=scheduler, args=(updater.bot,)).start()

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
