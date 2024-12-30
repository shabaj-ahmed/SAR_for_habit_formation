import time
import threading

import anki_vector

from src.robot_control import VectorRobotController
from src.communication_interface import CommunicationInterface

import logging

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
sys.path.insert(0, project_root)

from shared_libraries.logging_config import setup_logger
from shared_libraries.event_dispatcher import EventDispatcher

def publish_heartbeat():
    while True:
        # Publish robot controller heartbeat
        logger.info("Robot controller heartbeat")
        time.sleep(30)  # Publish heartbeat every 30 seconds

if __name__ == '__main__':
    try:
        setup_logger()

        logger = logging.getLogger("Main")

        dispatcher = EventDispatcher()

        controller = VectorRobotController(dispatcher)
        
        communication_interface = CommunicationInterface(
            broker_address=str(os.getenv("MQTT_BROKER_ADDRESS")),
            port=int(os.getenv("MQTT_BROKER_PORT")),
            event_dispatcher=dispatcher
        )

        communication_interface.publish_robot_status("Awake")

        heart_beat_thread = threading.Thread(target=publish_heartbeat, daemon=True)
        heart_beat_thread.start()
        # video_thread = threading.Thread(target=communication_interface.video_stream)
        # video_thread.start()

        while True:
            pass

    except KeyboardInterrupt as e:
        # Stop video streaming
        # controller.stop_video_stream()
        heart_beat_thread.join()
        # video_thread.join()
    except anki_vector.exceptions.VectorConnectionException as e:
        sys.exit("A connection error occurred: %s" % e)
        controller.disconnect_robot()
