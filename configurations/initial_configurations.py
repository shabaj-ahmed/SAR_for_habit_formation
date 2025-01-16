class StudyConfigs:
    def __init__(self):
        self.start_date = "2025-01-01"
        self.study_duration = 21
        self.user_name = "anonymous"
        self.reminder_time = {
            "hours": 3,
            "minutes": 0,
            "ampm": "PM"
        }
        self.implementation_intention = "I will exercise for 30 minutes every day at 8:00 AM"
        self.system_sleep_timer = 5
        self.brightness = 15
    
    def get_study_duration(self):
        return self.study_duration
    
    def get_start_date(self):
        return self.start_date
    
    def get_user_name(self):    
        return self.user_name
    
    def get_reminder_time(self):
        return self.reminder_time
    
    def get_implementation_intention(self):
        return self.implementation_intention
    
    def get_system_sleep_timer(self):
        return self.system_sleep_timer
    
    def get_brightness(self):
        return self.brightness
        