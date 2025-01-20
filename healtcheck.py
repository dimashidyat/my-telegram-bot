import os
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class HealthCheck:
    def __init__(self):
        self.bot_token = os.getenv("BOT_TOKEN")
        self.chat_id = os.getenv("CHAT_ID")
        self.start_time = datetime.now()

    def check_bot_status(self) -> bool:
        """Check if bot is responding"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def send_status_report(self):
        """Send status report to admin"""
        try:
            uptime = datetime.now() - self.start_time
            status = "🟢 Online" if self.check_bot_status() else "🔴 Offline"
            
            message = (
                f"*🤖 BOT STATUS REPORT*\n\n"
                f"Status: {status}\n"
                f"Uptime: {uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            requests.post(url, json=data, timeout=10)
            
        except Exception as e:
            logger.error(f"Error sending status report: {e}")

    def start_monitoring(self, interval_minutes: int = 60):
        """Start periodic health checks"""
        import time
        
        while True:
            self.send_status_report()
            time.sleep(interval_minutes * 60) 
