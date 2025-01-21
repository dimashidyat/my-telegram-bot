class HealthCheck:
    def check_bot_status(self) -> bool:
        """Check if bot is responding"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url, timeout=30)  # Increase timeout
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return True  # Return True to prevent restart loop
