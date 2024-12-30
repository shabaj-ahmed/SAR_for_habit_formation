import time
import threading
from src.device_monitor import NetworkMonitor
from src.event_dispatcher import EventDispatcher
from src.communication_interface import CommunicationInterface

import logging

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
sys.path.insert(0, project_root)

from shared_libraries.logging_config import setup_logger

def publish_heartbeat():
    while True:
        logger.info("Peripherals heartbeat")
        # network_connection = network_monitor.check_internet_connection()
        time.sleep(120)  # Publish heartbeat every 2 minutes

if __name__ == "__main__":
    try:
        setup_logger()

        logger = logging.getLogger("Main")

        dispatcher = EventDispatcher()

        network_monitor = NetworkMonitor(
            event_dispatcher=dispatcher
        )

        communication_interface = CommunicationInterface(
                broker_address=str(os.getenv("MQTT_BROKER_ADDRESS")),
                port=int(os.getenv("MQTT_BROKER_PORT")),
                event_dispatcher=dispatcher
            )

        # Start heartbeat thread
        heart_beat_thread = threading.Thread(target=publish_heartbeat, daemon=True)
        heart_beat_thread.start()

        while True:
            time.sleep(0.4)

    except KeyboardInterrupt as e:
        heart_beat_thread.join()
