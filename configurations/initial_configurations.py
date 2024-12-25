class StudyConfigs:
    def __init__(self):
        self.start_date = "2021-01-01"
        self.study_duration = 30
        self.user_name = "anonymous"
        self.reminder_time = {
            "hours": 8,
            "minutes": 0,
            "ampm": "AM"
        }
        self.implementation_intention = ""
        self.sleep_timer = 5
    
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
    
    def get_sleep_timer(self):
        return self.sleep_timer