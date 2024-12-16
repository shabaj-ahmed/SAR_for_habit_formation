import datetime
import os
import sys
import logging
from src.communication_interface import CommunicationInterface
import time
import threading

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
sys.path.insert(0, project_root)
from shared_libraries.logging_config import setup_logger

setup_logger()

class Reminder:
    def __init__(self, initial_reminder_time):
        self.reminder_time = initial_reminder_time
        self.todays_reminder_sent = False
        self.reminder_date = datetime.datetime.now().date()
        self.enable_reminder = True

        self.logger = logging.getLogger(self.__class__.__name__)
    
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
            self.todays_reminder_sent = True
            self.logger.info("check in reminder sent")
            return True
        time.sleep(1)
        return False
    
    @is_reminder_enabled
    def send_reminder(self):
        now = datetime.datetime.now()
        self.todays_reminder_sent = True
        self.reminder_date = now.date()
        self.logger.info("Reminder sent")
    
    @is_reminder_enabled
    def set_reminder_time(self, hours = 0, minutes = 0, ampm = "AM"):
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

def publish_heartbeat():
    while True:
        # Publish heartbeat
        time.sleep(30)  # Publish heartbeat every 30 seconds


if __name__ == "__main__":
    reminder = Reminder(datetime.time(hour=8, minute=0))

    communication_interface = CommunicationInterface(
        broker_address = str(os.getenv("MQTT_BROKER_ADDRESS")),
        port = int(os.getenv("MQTT_BROKER_PORT")),
        reminder_controler = reminder
    )

    # Start heartbeat thread
    threading.Thread(target=publish_heartbeat, daemon=True).start()

    while True:
        try:
            if communication_interface.command == "start":
                reminder.check_time()
        except Exception as e:
            logging.error(f"Reminder failed: {e}")