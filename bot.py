from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import csv
import io

# Data laporan pempek
pempek_data = []

# Menu Utama
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Panduan Tes Kerja BUMN", callback_data='panduan_bumn')],
        [InlineKeyboardButton("Target Hidup", callback_data='target_hidup')],
        [InlineKeyboardButton("Tentang Diri", callback_data='tentang_diri')],
        [InlineKeyboardButton("Laporan Pempek", callback_data='laporan_pempek')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Selamat datang di bot pribadi Dimas Hidayatulloh!\n\nPilih menu di bawah ini:", reply_markup=reply_markup)

# Menu Panduan Tes Kerja BUMN
def panduan_bumn(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    text = """
**Panduan Tes Kerja BUMN**
1. Pelajari materi TPA (verbal, numerik, logika) dan gunakan aplikasi latihan online.
2. Latih kemampuan bahasa Inggris (TOEFL/IELTS).
3. Wawancara: fokus percaya diri, sikap sopan, dan jawaban yang jelas.

**Link Referensi dan Materi:**
- [Latihan Online TPA](https://contoh-link.com/tpa)
- [Materi Bahasa Inggris](https://contoh-link.com/english)
- [Tips Wawancara](https://contoh-link.com/wawancara)
    """
    keyboard = [[InlineKeyboardButton("Kembali ke Menu Utama", callback_data='start')]]
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Menu Target Hidup
def target_hidup(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    text = """
**Target Hidup Dimas Hidayatulloh**
1. **Karir**:
   - Melamar kerja ke BUMN, fokus BULOG, dalam 3 bulan.
2. **Bisnis**:
   - Mengembangkan usaha keluarga: pempek.
3. **Kehidupan Pribadi**:
   - Menikah di usia 25 tahun.
4. **Finansial**:
   - Melunasi cicilan motor Rp1,3 juta/bulan.
   - Membantu stabilitas keuangan keluarga.
    """
    keyboard = [[InlineKeyboardButton("Kembali ke Menu Utama", callback_data='start')]]
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Menu Tentang Diri
def tentang_diri(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    text = """
**Tentang Diri Dimas Hidayatulloh**
- **Nama**: Dimas Hidayatulloh  
- **Tanggal Lahir**: 16 September 2003  
- **Pendidikan**:  
  - D3 Teknologi Industri Benih, IPB (IPK 3.80, Cum Laude)  
- **Pengalaman Kerja**:  
  1. CS di Netciti Persada  
  2. Magang di IP2SIP Cipaku  
  3. Virtual internship di Bank Muamalat  
- **Prestasi**:  
  - Mantan atlet taekwondo nasional.  
  - Juara 3 Business Plan Competition.  
- **Kelebihan**:  
  - IQ 123 (top 7%), kreatif, dan ahli debat (MBTI ENTP-T).  
- **Kekurangan**:  
  - Pola tidur berantakan, kurang terorganisir, dan self-esteem rendah.  
    """
    keyboard = [[InlineKeyboardButton("Kembali ke Menu Utama", callback_data='start')]]
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Menu Laporan Pempek
def laporan_pempek(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    text = """
**Laporan Pempek**
Masukkan data penjualan pempek dengan format:
`nama_pempek,jumlah,harga`

Contoh:
Pempek Lenjer,3,15000

Gunakan tombol di bawah untuk melihat laporan.
    """
    keyboard = [
        [InlineKeyboardButton("Lihat Laporan", callback_data='lihat_laporan')],
        [InlineKeyboardButton("Kembali ke Menu Utama", callback_data='start')]
    ]
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Input Data Pempek
def input_data(update: Update, context: CallbackContext):
    try:
        data = update.message.text.split(",")
        nama = data[0].strip()
        jumlah = int(data[1].strip())
        harga = int(data[2].strip())
        pempek_data.append({"nama": nama, "jumlah": jumlah, "harga": harga})
        update.message.reply_text(f"Data berhasil ditambahkan:\nNama: {nama}\nJumlah: {jumlah}\nHarga: Rp{harga}")
    except:
        update.message.reply_text("Format salah! Gunakan format: nama_pempek,jumlah,harga")

# Lihat Laporan Pempek
def lihat_laporan(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if not pempek_data:
        query.edit_message_text("Belum ada data pempek.")
        return

    laporan = "Laporan Pempek:\n\n"
    total_pendapatan = 0
    for item in pempek_data:
        subtotal = item["jumlah"] * item["harga"]
        laporan += f"{item['nama']}: {item['jumlah']} pcs x Rp{item['harga']} = Rp{subtotal}\n"
        total_pendapatan += subtotal

    laporan += f"\n**Total Pendapatan: Rp{total_pendapatan}**"
    query.edit_message_text(laporan, parse_mode="Markdown")

# Callback Handler
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'start':
        start(update, context)
    elif query.data == 'panduan_bumn':
        panduan_bumn(update, context)
    elif query.data == 'target_hidup':
        target_hidup(update, context)
    elif query.data == 'tentang_diri':
        tentang_diri(update, context)
    elif query.data == 'laporan_pempek':
        laporan_pempek(update, context)
    elif query.data == 'lihat_laporan':
        lihat_laporan(update, context)

# Main Function
def main():
    # Masukkan token bot kamu di sini
    updater = Updater("YOUR_BOT_TOKEN_HERE", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, input_data))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
