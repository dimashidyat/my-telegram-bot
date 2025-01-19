from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
import datetime
import random

# Token dan Chat ID
TOKEN = "7092522264:AAHsi2KM-8D8XcfIg09vptDyHiB28lRKQJY"
CHAT_ID = "2031898002"
PHONE_NUMBER = "+6281776633344"
CHANNEL_URL = "https://t.me/latihansoalbumn2025"

# Data Penyimpanan
data_log = {"pengeluaran": [], "pemasukan": [], "aktivitas": []}
motivasi_list = [
    "Kegagalan adalah jalan menuju kesuksesan.",
    "Jangan pernah menyerah, sukses sudah menunggu di depan!",
    "Kamu lebih kuat dari apa yang kamu pikirkan.",
]

# Fungsi Log Aktivitas
def log(update: Update, context: CallbackContext):
    try:
        kategori = context.args[0].lower()
        deskripsi = " ".join(context.args[1:])
        waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if kategori == "minyak" and deskripsi not in ["masih", "habis"]:
            raise ValueError
        data_log["aktivitas"].append({"kategori": kategori, "deskripsi": deskripsi, "waktu": waktu})
        update.message.reply_text(f"Log aktivitas '{kategori}' berhasil disimpan dengan status '{deskripsi}'.")
    except:
        update.message.reply_text("Format salah! Gunakan: /log <kategori> <deskripsi>\n\nContoh untuk minyak: /log minyak habis")

# Fungsi Statistik Harian
def statistik(update: Update, context: CallbackContext):
    aktivitas = "\n".join(
        [f"{i+1}. [{a['kategori']}] {a['deskripsi']} - {a['waktu']}" for i, a in enumerate(data_log["aktivitas"])]
    )
    total_pengeluaran = sum(p["jumlah"] for p in data_log["pengeluaran"])
    total_pemasukan = sum(p["jumlah"] for p in data_log["pemasukan"])
    update.message.reply_text(
        f"""📊 *Statistik Harian:*
- Total Pengeluaran: Rp. {total_pengeluaran:,}
- Total Pemasukan: Rp. {total_pemasukan:,}

📝 *Log Aktivitas:*
{aktivitas if aktivitas else "Tidak ada aktivitas tercatat."}
        """,
        parse_mode=ParseMode.MARKDOWN,
    )

# Fungsi Latihan Soal BUMN
def soal_bumn(update: Update, context: CallbackContext):
    update.message.reply_text(
        f"📚 Soal latihan terbaru dapat diakses melalui channel berikut:\n{CHANNEL_URL}",
        parse_mode=ParseMode.MARKDOWN,
    )

# Fungsi Motivasi Harian
def motivasi(update: Update, context: CallbackContext):
    update.message.reply_text(random.choice(motivasi_list))

# Fungsi Auto Reminder
def auto_reminder(context: CallbackContext):
    pesan = f"⏰ Selamat pagi! Jangan lupa lakukan hal produktif hari ini. Semangat 💪\nHubungi saya di WhatsApp {PHONE_NUMBER} jika ada pertanyaan."
    context.bot.send_message(chat_id=CHAT_ID, text=pesan)

# Fungsi Pomodoro Timer
def pomodoro(update: Update, context: CallbackContext):
    try:
        waktu = int(context.args[0])  # Waktu dalam menit
        context.job_queue.run_once(
            pomodoro_selesai, waktu * 60, context=update.message.chat_id, name=str(update.message.chat_id)
        )
        update.message.reply_text(f"⏳ Pomodoro dimulai: {waktu} menit.")
    except:
        update.message.reply_text("Format salah! Gunakan: /pomodoro <waktu (menit)>")

def pomodoro_selesai(context: CallbackContext):
    context.bot.send_message(chat_id=context.job.context, text="⏰ Pomodoro selesai! Waktunya istirahat.")

# Fungsi Start
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Selamat datang di bot manajemen harian!\n\n"
        "📝 *Fitur Bot:*\n"
        "- /log <kategori> <deskripsi>: Tambah log aktivitas.\n"
        "- /statistik: Lihat statistik log harian.\n"
        "- /soal_bumn: Lihat soal latihan terbaru dari channel BUMN.\n"
        "- /motivasi: Dapatkan motivasi harian.\n"
        "- /pomodoro <waktu>: Timer belajar fokus.\n\n"
        "💡 Jangan lupa tetap produktif ya!"
    )

# Main Function
def main():
    # Menjalankan bot
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("log", log))
    dp.add_handler(CommandHandler("statistik", statistik))
    dp.add_handler(CommandHandler("soal_bumn", soal_bumn))
    dp.add_handler(CommandHandler("motivasi", motivasi))
    dp.add_handler(CommandHandler("pomodoro", pomodoro))

    # Scheduler untuk Auto Reminder
    scheduler = BackgroundScheduler(executors={"default": ThreadPoolExecutor(10)})
    scheduler.add_job(auto_reminder, "cron", hour=5, minute=0, args=[updater.bot])
    scheduler.start()

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
