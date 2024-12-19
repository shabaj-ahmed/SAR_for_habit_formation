import datetime
import os
import sys
import logging
from src.reminder_controller import ReminderController
from src.communication_interface import CommunicationInterface
import time
import threading
from src.event_dispatcher import EventDispatcher

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
sys.path.insert(0, project_root)
from shared_libraries.logging_config import setup_logger

setup_logger()

def publish_heartbeat():
    while True:
        # Publish heartbeat
        time.sleep(30)  # Publish heartbeat every 30 seconds

if __name__ == "__main__":
    dispatcher = EventDispatcher()

    reminder = ReminderController(datetime.time(hour=8, minute=30), dispatcher)

    communication_interface = CommunicationInterface(
        broker_address = str(os.getenv("MQTT_BROKER_ADDRESS")),
        port = int(os.getenv("MQTT_BROKER_PORT")),
        event_dispatcher=dispatcher
    )

    # Start heartbeat thread
    threading.Thread(target=publish_heartbeat, daemon=True).start()

    while True:
        try:
            if communication_interface.command == "start":
                reminder.check_time()
        except Exception as e:
            logging.error(f"Reminder failed: {e}")