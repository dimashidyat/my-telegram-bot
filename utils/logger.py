import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # Console handler
        logging.StreamHandler(),
        # File handler
        logging.FileHandler(
            f'logs/bot_{datetime.now().strftime("%Y%m%d")}.log'
        )
    ]
)

logger = logging.getLogger(__name__)

def log_start():
    """Log bot startup"""
    logger.info("Bot starting...")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Files in current directory: {os.listdir('.')}")

def log_error(error: Exception):
    """Log error with full traceback"""
    logger.error(f"Error occurred: {str(error)}", exc_info=True)
