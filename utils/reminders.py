from datetime import datetime, time

class ReminderSystem:
    def __init__(self):
        self.default_times = {
            'subuh': time(4, 45),
            'maxim': time(7, 0),
            'study': time(10, 0),
            'pempek': time(21, 0)
        }
        
    def get_next_reminder(self):
        now = datetime.now().time()
        next_reminder = None
        
        for activity, reminder_time in self.default_times.items():
            if now < reminder_time:
                next_reminder = (activity, reminder_time)
                break
                
        return next_reminder
