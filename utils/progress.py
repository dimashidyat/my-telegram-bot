class ProgressTracker:
    def __init__(self):
        self.metrics = {
            'study': {
                'daily_target': 2,  # jam
                'completed': 0,
                'streak': 0
            },
            'health': {
                'workout_target': 30,  # menit
                'sleep_target': 6,    # jam
                'completed': 0
            },
            'income': {
                'maxim_target': 50000,
                'earned': 0
            }
        }
        
    def update_progress(self, category, value):
        """Update progress for specific category"""
        if category in self.metrics:
            self.metrics[category]['completed'] += value
            
            # Update streak if applicable
            if category == 'study' and value > 0:
                self.metrics[category]['streak'] += 1
            elif category == 'study':
                self.metrics[category]['streak'] = 0
                
        return self.get_progress(category)
        
    def get_progress(self, category):
        """Get progress percentage for category"""
        if category not in self.metrics:
            return 0
            
        metric = self.metrics[category]
        target = metric.get('daily_target', 0)
        
        if target == 0:
            return 0
            
        return (metric['completed'] / target) * 100
