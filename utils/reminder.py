import logging
from datetime import datetime, time, timedelta
from telegram import Bot
from telegram.ext import ContextTypes
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ReminderSystem:
    def __init__(self):
        self.reminders: Dict[str, Dict[str, Any]] = {}
        
        # Default reminder times
        self.default_times = {
            'subuh': time(4, 45),
            'morning': time(7, 0),
            'study': time(10, 0),
            'dzuhur': time(12, 0),
            'ashar': time(15, 0),
            'maghrib': time(18, 0),
            'isya': time(19, 0),
            'sleep': time(22, 0)
        }
        
        # Reminder messages
        self.messages = {
            'subuh': "🌅 Waktunya Sholat Subuh!\n\nJangan lupa:\n• Sholat Subuh\n• Dzikir pagi\n• Olahraga ringan",
            'morning': "☀️ Good Morning!\n\nAgenda hari ini:\n• Maxim (target 50k)\n• Belajar BULOG\n• Dagang pempek",
            'study': "📚 Waktunya Belajar!\n\nTarget hari ini:\n• TWK: 20 soal\n• TIU: 15 soal\n• TKP: 10 soal",
            'dzuhur': "🕌 Waktunya Sholat Dzuhur!\n\nJangan lupa:\n• Sholat Dzuhur\n• Makan siang\n• Break sejenak",
            'ashar': "🕌 Waktunya Sholat Ashar!\n\nJangan lupa:\n• Sholat Ashar\n• Input laporan pempek\n• Update stok",
            'maghrib': "🕌 Waktunya Sholat Maghrib!\n\nJangan lupa:\n• Sholat Maghrib\n• Dzikir sore\n• Persiapan tutup",
            'isya': "🕌 Waktunya Sholat Isya!\n\nJangan lupa:\n• Sholat Isya\n• Review target harian\n• Quality time",
            'sleep': "😴 Waktunya Tidur!\n\nJangan lupa:\n• Wudhu\n• Baca Al-Kahfi\n• Tidur menghadap kanan",
        }

    async def set_reminder(
        self,
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int,
        reminder_type: str,
        custom_time: Optional[time] = None,
        custom_message: Optional[str] = None
    ):
        """Set a reminder"""
        try:
            reminder_time = custom_time or self.default_times.get(reminder_type)
            message = custom_message or self.messages.get(reminder_type)
            
            if not reminder_time or not message:
                logger.error(f"Invalid reminder type: {reminder_type}")
                return False

            # Calculate next occurrence
            now = datetime.now()
            target_time = datetime.combine(now.date(), reminder_time)
            
            if target_time < now:
                target_time += timedelta(days=1)

            # Schedule reminder
            context.job_queue.run_daily(
                self.send_reminder,
                time=reminder_time,
                chat_id=chat_id,
                data={
                    'type': reminder_type,
                    'message': message
                }
            )

            # Save reminder info
            self.reminders[f"{chat_id}_{reminder_type}"] = {
                'chat_id': chat_id,
                'type': reminder_type,
                'time': reminder_time.strftime('%H:%M'),
                'message': message
            }

            return True

        except Exception as e:
            logger.error(f"Error setting reminder: {e}")
            return False

    async def send_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        """Send reminder message"""
        job = context.job
        chat_id = job.chat_id
        reminder_data = job.data

        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=reminder_data['message'],
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")

    def get_active_reminders(self, chat_id: int) -> Dict[str, Any]:
        """Get all active reminders for a chat"""
        return {
            k: v for k, v in self.reminders.items()
            if v['chat_id'] == chat_id
        }

    async def clear_reminder(
        self,
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int,
        reminder_type: str
    ) -> bool:
        """Clear a specific reminder"""
        try:
            reminder_key = f"{chat_id}_{reminder_type}"
            
            if reminder_key in self.reminders:
                # Remove from job queue
                current_jobs = context.job_queue.get_jobs_by_name(reminder_key)
                for job in current_jobs:
                    job.schedule_removal()
                
                # Remove from reminders dict
                del self.reminders[reminder_key]
                return True
                
            return False

        except Exception as e:
            logger.error(f"Error clearing reminder: {e}")
            return False

    async def clear_all_reminders(
        self,
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int
    ) -> bool:
        """Clear all reminders for a chat"""
        try:
            # Get all reminders for this chat
            chat_reminders = self.get_active_reminders(chat_id)
            
            # Clear each reminder
            for reminder_key in chat_reminders:
                reminder_type = reminder_key.split('_')[1]
                await self.clear_reminder(context, chat_id, reminder_type)
                
            return True

        except Exception as e:
            logger.error(f"Error clearing all reminders: {e}")
            return False 
