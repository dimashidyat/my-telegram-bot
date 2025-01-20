from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
import logging
import json
import random

logger = logging.getLogger(__name__)

class HealthHandler:
    def __init__(self):
        self.health_data = {}
        
        # Smart workout plans sesuai waktu
        self.quick_workouts = {
            'pagi': [
                {
                    'name': 'Morning Power',
                    'exercises': [
                        ('Push Up', 10, 'Setelah Subuh'),
                        ('Plank', 30, 'seconds'),
                        ('Jumping Jack', 20, 'reps')
                    ],
                    'duration': '5-7 menit'
                },
                {
                    'name': 'Maxim Warm Up',
                    'exercises': [
                        ('Stretching', 2, 'minutes'),
                        ('Light Jogging', 5, 'minutes'),
                        ('Jumping', 20, 'reps')
                    ],
                    'duration': '8-10 menit'
                }
            ],
            'siang': [
                {
                    'name': 'Break Time Burn',
                    'exercises': [
                        ('Office Chair Squat', 15, 'reps'),
                        ('Desk Push Up', 10, 'reps'),
                        ('Standing Twist', 20, 'reps')
                    ],
                    'duration': '3-5 menit'
                }
            ],
            'malam': [
                {
                    'name': 'Evening Relaxer',
                    'exercises': [
                        ('Light Stretching', 5, 'minutes'),
                        ('Deep Breathing', 2, 'minutes'),
                        ('Simple Yoga', 3, 'poses')
                    ],
                    'duration': '10 menit'
                }
            ]
        }

        # Target goals dengan adaptive system
        self.base_goals = {
            'workout': {'min': 30, 'max': 60, 'unit': 'menit', 'increment': 5},
            'sleep': {'min': 6, 'max': 8, 'unit': 'jam', 'increment': 0.5},
            'water': {'min': 2, 'max': 3, 'unit': 'liter', 'increment': 0.25},
            'calories': {'min': 300, 'max': 500, 'unit': 'kcal', 'increment': 50}
        }

        # Exercise database dengan kalori & tips
        self.exercises = {
            'pushup': {
                'name': 'Push Up',
                'calories_per_rep': 0.5,
                'difficulty': 'medium',
                'muscles': ['chest', 'triceps', 'shoulders'],
                'tips': [
                    'Jaga punggung tetap lurus',
                    'Turunkan dada sampai hampir menyentuh lantai',
                    'Napas teratur: turun = tarik napas, naik = buang napas'
                ],
                'variations': [
                    'Knee push up (lebih mudah)',
                    'Diamond push up (triceps focus)',
                    'Wide push up (chest focus)'
                ]
            },
            'plank': {
                'name': 'Plank',
                'calories_per_minute': 5,
                'difficulty': 'easy',
                'muscles': ['core', 'shoulders', 'back'],
                'tips': [
                    'Pastikan tubuh membentuk garis lurus',
                    'Aktifkan otot perut',
                    'Tahan napas stabil'
                ],
                'variations': [
                    'Side plank',
                    'Plank dengan angkat kaki',
                    'Plank to downward dog'
                ]
            },
            'squat': {
                'name': 'Squat',
                'calories_per_rep': 0.45,
                'difficulty': 'medium',
                'muscles': ['legs', 'glutes', 'core'],
                'tips': [
                    'Turunkan pinggul sejajar lutut',
                    'Jaga lutut sejajar dengan jari kaki',
                    'Pandangan lurus ke depan'
                ],
                'variations': [
                    'Jump squat',
                    'Sumo squat',
                    'Single leg squat'
                ]
            }
        }

        # Motivational messages
        self.motivations = {
            'start_workout': [
                "💪 Gas bro! Cuma {duration} menit doang nih",
                "🔥 Jangan kasih kendor! {duration} menit = {calories} kalori",
                "⚡ Quick workout dulu {duration} menit, habis itu lanjut aktivitas"
            ],
            'finish_workout': [
                "🎯 Mantap! Udah bakar {calories} kalori nih",
                "🚀 Level up! Total workout minggu ini: {weekly_minutes} menit",
                "💪 Konsisten bro! Streak: {streak} hari"
            ],
            'sleep_reminder': [
                "😴 Udah jam {time} nih, siap-siap bobo bro",
                "🌙 Quality sleep = Better gains! Yuk tidur",
                "💤 Besok pagi ada Maxim, istirahat dulu ya"
            ]
        }

    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Smart health menu with time-based recommendations"""
        try:
            user_id = update.effective_user.id
            current_hour = datetime.now().hour
            
            # Get appropriate workout based on time
            if 4 <= current_hour < 10:
                time_period = 'pagi'
                recommended = self.quick_workouts['pagi']
            elif 10 <= current_hour < 18:
                time_period = 'siang'
                recommended = self.quick_workouts['siang']
            else:
                time_period = 'malam'
                recommended = self.quick_workouts['malam']

            # Get user's stats
            stats = self.get_user_stats(user_id)
            workout = random.choice(recommended)

            keyboard = [
                [
                    InlineKeyboardButton("💪 Quick Workout", callback_data=f"health_quick_{time_period}"),
                    InlineKeyboardButton("📊 Progress", callback_data="health_progress")
                ],
                [
                    InlineKeyboardButton("⚡ Custom Workout", callback_data="health_custom"),
                    InlineKeyboardButton("📈 Statistik", callback_data="health_stats")
                ],
                [
                    InlineKeyboardButton("🎯 Set Target", callback_data="health_goals"),
                    InlineKeyboardButton("💡 Tips", callback_data="health_tips")
                ],
                [InlineKeyboardButton("🔙 Menu Utama", callback_data="back_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            text = (
                f"*💪 HEALTH TRACKER*\n\n"
                f"*Quick Workout {time_period.title()}:*\n"
                f"• {workout['name']}\n"
                f"• Durasi: {workout['duration']}\n"
                f"• Kalori: ~{self.calculate_calories(workout)} kcal\n\n"
                "*Progress Hari Ini:*\n"
                f"• Workout: {stats['today_workout']}/{stats['workout_target']} menit\n"
                f"• Kalori: {stats['today_calories']}/{stats['calorie_target']} kcal\n"
                f"• Streak: {stats['streak']} hari\n\n"
                "*💪 Achievement:*\n"
                f"• Level: {self.calculate_level(stats['total_workouts'])}\n"
                f"• Next: {stats['next_milestone']} workout lagi"
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
            await self.handle_error(update, "Gagal menampilkan menu health")

    def calculate_calories(self, workout: dict) -> int:
        """Calculate estimated calories for a workout"""
        base_calories = {
            'Push Up': 0.5,  # per rep
            'Plank': 0.1,    # per second
            'Jumping Jack': 0.2,  # per rep
            'Squat': 0.45    # per rep
        }
        
        total = 0
        for exercise, count, unit in workout['exercises']:
            if exercise in base_calories:
                if unit == 'seconds':
                    total += base_calories[exercise] * count
                else:  # reps
                    total += base_calories[exercise] * count
                    
        return round(total)

    def calculate_level(self, total_workouts: int) -> int:
        """Calculate user's fitness level"""
        base_xp = 100
        level = 1
        while total_workouts >= base_xp:
            total_workouts -= base_xp
            base_xp *= 1.5
            level += 1
        return level

    async def start_quick_workout(self, update: Update, context: ContextTypes.DEFAULT_TYPE, time_period: str):
        """Start a quick workout session"""
        try:
            workout = random.choice(self.quick_workouts[time_period])
            user_id = update.effective_user.id
            
            # Save workout state
            self.health_data[user_id] = {
                'current_workout': workout,
                'start_time': datetime.now(),
                'exercises_done': 0
            }
            
            # Create exercise buttons
            keyboard = []
            for i, (exercise, count, unit) in enumerate(workout['exercises']):
                keyboard.append([
                    InlineKeyboardButton(
                        f"✅ {exercise} - {count} {unit}",
                        callback_data=f"workout_done_{i}"
                    )
                ])
            keyboard.append([InlineKeyboardButton("🏁 Selesai", callback_data="workout_finish")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Get random motivation message
            motivation = random.choice(self.motivations['start_workout'])
            motivation = motivation.format(
                duration=workout['duration'],
                calories=self.calculate_calories(workout)
            )
            
            text = (
                f"*💪 {workout['name']}*\n\n"
                f"{motivation}\n\n"
                "*Workout Plan:*\n"
            )
            
            for exercise, count, unit in workout['exercises']:
                text += f"• {exercise}: {count} {unit}\n"
                
            text += f"\nKlik ✅ setiap selesai gerakan ya!"
                
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error starting workout: {e}")
            await self.handle_error(update, "Gagal memulai workout")

    def get_user_stats(self, user_id: int) -> dict:
        """Get user's health statistics"""
        if user_id not in self.health_data:
            return {
                'today_workout': 0,
                'today_calories': 0,
                'workout_target': 30,
                'calorie_target': 300,
                'streak': 0,
                'total_workouts': 0,
                'next_milestone': 100
            }
            
        data = self.health_data[user_id]
        total_workouts = data.get('total_workouts', 0)
        next_milestone = (total_workouts // 100 + 1) * 100
        
        return {
            'today_workout': data.get('today_workout', 0),
            'today_calories': data.get('today_calories', 0),
            'workout_target': data.get('workout_target', 30),
            'calorie_target': data.get('calorie_target', 300),
            'streak': data.get('streak', 0),
            'total_workouts': total_workouts,
            'next_milestone': next_milestone - total_workouts
        }

    async def handle_error(self, update: Update, message: str):
        """Handle errors with recovery options"""
        error_text = (
            f"❌ {message}\n\n"
            "Options:\n"
            "1. Ketik /start\n"
            "2. Pilih menu Health lagi\n"
            "3. Hubungi developer kalau masih error"
        )
        
        if update.callback_query:
            await update.callback_query.message.reply_text(error_text)
        else:
            await update.message.reply_text(error_text)

    def save_data(self):
        """Save health data to file"""
        try:
            with open('health_data.json', 'w') as f:
                json.dump(self.health_data, f)
        except Exception as e:
            logger.error(f"Error saving health data: {e}")

    def load_data(self):
        """Load health data from file"""
        try:
            with open('health_data.json', 'r') as f:
                self.health_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading health data: {e}")
            self.health_data = {}
