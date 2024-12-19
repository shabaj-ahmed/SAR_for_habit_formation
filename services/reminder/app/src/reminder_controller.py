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

        self.logger = logging.getLogger(self.__class__.__name__)
        self._register_event_handlers()

    def _register_event_handlers(self):
        if self.dispatcher:
            self.dispatcher.register_event("set_reminder", self.set_reminder_time)
    
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