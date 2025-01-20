import logging
from typing import Dict, List, Optional
import random

logger = logging.getLogger(__name__)

class AIChat:
    def __init__(self):
        self.conversation_history = {}
        
        # Templates untuk berbagai konteks
        self.templates = {
            'greeting': [
                "Assalamualaikum bro! Ada yang bisa dibantu?",
                "Hai bro! Mau ngapain nih hari ini?",
                "Selamat datang! Mau mulai dari mana nih?"
            ],
            'study': [
                "Semangat belajarnya bro! Target hari ini {target} soal ya",
                "Focus mode: ON 💪 Yuk belajar {duration} menit",
                "Break time! Udah {completed} soal, mantap 👍"
            ],
            'pempek': [
                "Waktunya input laporan nih! Jangan lupa:",
                "Ada {items} yang perlu diinput",
                "Total setoran hari ini: {amount}"
            ],
            'motivation': [
                "Ingat BULOG bro! 💪",
                "Bismillah, pasti bisa! 🚀",
                "Step by step kita capai target 🎯"
            ],
            'reminder': [
                "⏰ Jangan lupa {task}!",
                "Waktunya {task} bro!",
                "Reminder: {task} sekarang ya"
            ]
        }

    def get_response(self, user_id: str, context: str, **kwargs) -> str:
        """Get contextual response"""
        try:
            if context in self.templates:
                template = random.choice(self.templates[context])
                return template.format(**kwargs)
            return "Maaf, saya tidak mengerti konteksnya"
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Ada error nih, coba lagi ya"

    def get_greeting(self, user_id: str, time_of_day: str) -> str:
        """Get time-appropriate greeting"""
        greetings = {
            'morning': [
                "Pagi bro! Jangan lupa sarapan ya",
                "Selamat pagi! Ready untuk hari ini?",
                "Good morning! Mari kita mulai hari dengan semangat"
            ],
            'afternoon': [
                "Siang bro! Udah makan siang belum?",
                "Met siang! Jangan lupa istirahat ya",
                "Selamat siang! Keep the spirit up!"
            ],
            'evening': [
                "Sore bro! Gimana progress hari ini?",
                "Selamat sore! Mari review target harian",
                "Good evening! Semangat untuk sisa harinya"
            ],
            'night': [
                "Malam bro! Jangan begadang ya",
                "Met malam! Waktunya istirahat yang cukup",
                "Good night! Persiapkan energi untuk besok"
            ]
        }
        
        try:
            return random.choice(greetings.get(time_of_day, self.templates['greeting']))
        except Exception as e:
            logger.error(f"Error getting greeting: {e}")
            return random.choice(self.templates['greeting'])

    def get_study_motivation(self, progress: Dict) -> str:
        """Get study motivation based on progress"""
        try:
            if progress['completed'] == 0:
                return "Yuk mulai belajar! Take it step by step 💪"
            elif progress['completed'] < progress['target'] // 2:
                return f"Udah {progress['completed']} soal, lanjutkan! 🚀"
            elif progress['completed'] < progress['target']:
                return f"Tinggal {progress['target'] - progress['completed']} soal lagi! 🎯"
            else:
                return "Mantap! Target tercapai, istirahat dulu ya 🌟"
        except Exception as e:
            logger.error(f"Error getting study motivation: {e}")
            return "Semangat belajarnya! 💪"

    def get_reminder_message(self, task: str, deadline: Optional[str] = None) -> str:
        """Get reminder message"""
        try:
            base_message = f"⏰ REMINDER: {task}"
            if deadline:
                base_message += f"\nDeadline: {deadline}"
            return base_message
        except Exception as e:
            logger.error(f"Error getting reminder: {e}")
            return f"Reminder: {task}"
