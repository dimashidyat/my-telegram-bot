import logging
from datetime import datetime, date
from typing import Dict, Any, Optional
import json
import os

logger = logging.getLogger(__name__)

class ProgressTracker:
    def __init__(self):
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        self.progress_file = os.path.join(self.data_dir, "progress.json")
        self.load_data()

    def load_data(self):
        """Load progress data"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    self.data = json.load(f)
            else:
                self.data = {}
        except Exception as e:
            logger.error(f"Error loading progress data: {e}")
            self.data = {}

    def save_data(self):
        """Save progress data"""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving progress data: {e}")

    def update_study_progress(
        self,
        user_id: str,
        category: str,
        completed: int,
        total_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """Update study progress"""
        try:
            if user_id not in self.data:
                self.data[user_id] = {}
            
            if 'study' not in self.data[user_id]:
                self.data[user_id]['study'] = {
                    'TWK': {'completed': 0, 'streak': 0},
                    'TIU': {'completed': 0, 'streak': 0},
                    'TKP': {'completed': 0, 'streak': 0},
                    'total_time': 0,
                    'last_study': None
                }

            study_data = self.data[user_id]['study']
            
            # Update completion
            if category in study_data:
                study_data[category]['completed'] += completed
                
                # Update streak if studied today
                today = date.today().isoformat()
                if study_data['last_study'] != today:
                    study_data[category]['streak'] += 1
                    study_data['last_study'] = today

            # Update study time
            if total_time:
                study_data['total_time'] += total_time

            self.save_data()
            return study_data

        except Exception as e:
            logger.error(f"Error updating study progress: {e}")
            return {}

    def update_income_progress(
        self,
        user_id: str,
        source: str,
        amount: int
    ) -> Dict[str, Any]:
        """Update income progress"""
        try:
            if user_id not in self.data:
                self.data[user_id] = {}
            
            if 'income' not in self.data[user_id]:
                self.data[user_id]['income'] = {
                    'maxim': {'daily': 0, 'total': 0},
                    'pempek': {'daily': 0, 'total': 0},
                    'last_update': None
                }

            income_data = self.data[user_id]['income']
            
            # Reset daily if new day
            today = date.today().isoformat()
            if income_data['last_update'] != today:
                income_data['maxim']['daily'] = 0
                income_data['pempek']['daily'] = 0
                income_data['last_update'] = today

            # Update income
            if source in ['maxim', 'pempek']:
                income_data[source]['daily'] += amount
                income_data[source]['total'] += amount

            self.save_data()
            return income_data

        except Exception as e:
            logger.error(f"Error updating income progress: {e}")
            return {}

    def update_health_progress(
        self,
        user_id: str,
        activity_type: str,
        duration: int = 0,
        sleep_hours: float = 0
    ) -> Dict[str, Any]:
        """Update health progress"""
        try:
            if user_id not in self.data:
                self.data[user_id] = {}
            
            if 'health' not in self.data[user_id]:
                self.data[user_id]['health'] = {
                    'workout': {'daily': 0, 'total': 0, 'streak': 0},
                    'sleep': {'hours': 0, 'quality': 'N/A', 'streak': 0},
                    'last_update': None
                }

            health_data = self.data[user_id]['health']
            
            today = date.today().isoformat()
            if health_data['last_update'] != today:
                health_data['workout']['daily'] = 0
                health_data['sleep']['hours'] = 0
                health_data['last_update'] = today

            if activity_type == 'workout':
                health_data['workout']['daily'] += duration
                health_data['workout']['total'] += duration
                if duration > 0:
                    health_data['workout']['streak'] += 1
            elif activity_type == 'sleep':
                health_data['sleep']['hours'] = sleep_hours
                if 6 <= sleep_hours <= 8:
                    health_data['sleep']['quality'] = 'Good'
                    health_data['sleep']['streak'] += 1
                else:
                    health_data['sleep']['quality'] = 'Poor'
                    health_data['sleep']['streak'] = 0

            self.save_data()
            return health_data

        except Exception as e:
            logger.error(f"Error updating health progress: {e}")
            return {}
