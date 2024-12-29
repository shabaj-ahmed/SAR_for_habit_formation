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

# def publish_heartbeat():
#     while True:
#         logger.info("Peripherals heartbeat")
#         network_connection = network_monitor.check_internet_connection()
#         time.sleep(120)  # Publish heartbeat every 2 minutes

# if __name__ == "__main__":
#     setup_logger()

#     logger = logging.getLogger("Main")

#     dispatcher = EventDispatcher()

#     network_monitor = NetworkMonitor(
#         event_dispatcher=dispatcher
#     )

#     communication_interface = CommunicationInterface(
#             broker_address=str(os.getenv("MQTT_BROKER_ADDRESS")),
#             port=int(os.getenv("MQTT_BROKER_PORT")),
#             event_dispatcher=dispatcher
#         )

#     # Start heartbeat thread
#     threading.Thread(target=publish_heartbeat, daemon=True).start()

#     while True:
#         try:
#             if communication_interface.command == "start":
#                 network_monitor.run_speed_test()
#                 results_dict = network_monitor.get_results()
#         except Exception as e:
#             logging.error(f"Reminder failed: {e}")
#         time.sleep(0.2)