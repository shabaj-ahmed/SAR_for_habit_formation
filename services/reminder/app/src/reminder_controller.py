import datetime
import time
import logging

class ReminderController:
    def __init__(self, initial_reminder_time, event_dispatcher):
        self.reminder_time = initial_reminder_time
        self.dispatcher = event_dispatcher
        self.todays_reminder_sent = False
        self.reminder_date = datetime.datetime.now().date()
        self.enable_reminder = True
        self.user_name = ""
        self.study_duration = 0
        self.start_date = None

        self.logger = logging.getLogger(self.__class__.__name__)
        self._register_event_handlers()
    
    def _register_event_handlers(self):
        if self.dispatcher:
            self.dispatcher.register_event("set_reminder", self.set_reminder_time)
            self.dispatcher.register_event("update_service_state", self._update_service_state)
    
    def _update_service_state(self, payload):
        self.logger.info(f"State update received in Reminder: {payload}")
        state_name = payload.get("state_name", "")
        state_value = payload.get("state_value", "")
        if state_name == "user_name":
            self.user_name = state_value
            self.logger.info(f"User name updated: {self.user_name}")
        elif state_name == "study_duration":
            self.study_duration = state_value
            self.logger.info(f"Study duration updated: {self.study_duration}")
        elif state_name == "reminder_time_hr":
            self.reminder_time = self.reminder_time.replace(hour=int(state_value))
            self.logger.info(f"Reminder time updated to {self.reminder_time}")
        elif state_name == "reminder_time_min":
            self.reminder_time = self.reminder_time.replace(minute=int(state_value))
            self.logger.info(f"Reminder time updated to {self.reminder_time}")
        elif state_name == "reminder_time_ampm":
            if state_value == "PM" and self.reminder_time.hour < 12:
                self.reminder_time = self.reminder_time.replace(hour=self.reminder_time.hour + 12)
                self.logger.info(f"Reminder time updated to {self.reminder_time}")
        elif state_name == "start_date":
            self.start_date = datetime.datetime.strptime(state_value, "%Y-%m-%d").date()
            self.logger.info(f"Start date updated to {self.start_date}")
    
    def is_reminder_enabled(func):
        '''
        Decorator to enable the reminder.
        '''
        def wrapper(self, *args, **kwargs):
            try:
                if self.enable_reminder:
                    # self.logger.info("Reminder enabled")
                    return func(self, *args, **kwargs)
            except Exception as e:
                self.logger.error(f"Reminder failed: {e}")
                raise e
            return None  # Or raise another custom exception if necessary
        return wrapper
    
    @is_reminder_enabled
    def check_time(self):
        # Look in database to check if the reminder has been sent today
            # Reset reminder if it has been sent
        self._reset_reminder()
        now = datetime.datetime.now().time()
        if now > self.reminder_time and not self.todays_reminder_sent:
            self.send_reminder()
            return True
        time.sleep(1)
        return False
    
    @is_reminder_enabled
    def send_reminder(self):
        now = datetime.datetime.now()
        self.reminder_date = now.date()
        self.dispatcher.dispatch_event("send_reminder")
        self.todays_reminder_sent = True
    
    @is_reminder_enabled
    def set_reminder_time(self, time):
        hours = int(time.get("hours", 0))
        minutes = int(time.get("minutes", 0))
        ampm = time.get("ampm", "AM")

        if ampm == "PM" and hours < 12:
            hours += 12
        self.reminder_time = datetime.time(hour=hours, minute=minutes)
        self.reminder_date = datetime.datetime.now().date()
        self.logger.info(f"Reminder set for {self.reminder_time}")
    
    @is_reminder_enabled
    def _reset_reminder(self):
        now = datetime.datetime.now()
        current_date = now.date()

        if self.reminder_date is not None and current_date > self.reminder_date and self.todays_reminder_sent:
            self.todays_reminder_sent = False
            self.logger.info("Reminder reset")