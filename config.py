import os
from datetime import time, date

# Bot Config
TOKEN = "7092522264:AAHsi2KM-8D8XcfIg09vptDyHiB28lRKQJY"
CHAT_ID = "2031898002"

# Personal Data
GIRLFRIEND_PHONE = "6281513607410"
MY_PHONE = "6281776633344"
ANNIVERSARY_DATE = date(2021, 9, 13)

# Telegram Channels
CHANNELS = {
    'bumn': '@latihansoalbumn2025',
    'backup': ['@infocpnsbumn', '@cpnsindonesia']
}

# Schedule Settings
JADWAL = {
    'pagi': {
        'subuh': time(4, 45),
        'maxim': time(7, 0),
        'study': time(10, 0)
    },
    'siang': {
        'dzuhur': time(12, 0),
        'break': time(12, 30),
        'ashar': time(15, 0)
    },
    'malam': {
        'maghrib': time(18, 0),
        'isya': time(19, 0),
        'pempek_report': time(21, 0),
        'sleep': time(22, 0)
    }
}

# Study Categories
STUDY_MATERIALS = {
    'TWK': ['Pancasila', 'UUD 1945', 'Sejarah'],
    'TIU': ['Matematika', 'Verbal', 'Logika'],
    'TKP': ['Karakteristik Pribadi', 'Integritas']
}

# Prices
PEMPEK_PRICES = {
    'kecil': 2500,
    'gede': 12000,
    'items': {
        'air': 4000,
        'gas': 22000,
        'plastik': 2000,
        'es': 3000
    }
}

# Health Goals
HEALTH_GOALS = {
    'workout': {'target': 30, 'unit': 'menit'},
    'sleep': {'target': 6, 'unit': 'jam'},
    'water': {'target': 2, 'unit': 'liter'}
}
