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
        time.sleep(20)  # Publish heartbeat every 30 seconds
        status = "disconnected"
        if controller.connected:
            robot_is_connected = controller.check_connection()
            status = "connected" if robot_is_connected else "disconnected"
        communication_interface.publish_robot_connection_status(status)
        logger.info(f"Robot controller heartbeat, the robot is currently {status}")


if __name__ == '__main__':
    try:
        setup_logger()

        logger = logging.getLogger("Main")

        dispatcher = EventDispatcher()

        controller = VectorRobotController()

        communication_interface = CommunicationInterface(
            broker_address=str(os.getenv("MQTT_BROKER_ADDRESS")),
            port=int(os.getenv("MQTT_BROKER_PORT")),
            controller=controller,
        )

        controller.communication_interface = communication_interface
        logger.info("Requesting a connection to the robot")
        controller.connect()
        logger.info("Connection request has completed...")
        while not controller.connected:
            pass
        logger.info("################## Connected to robot}")
        resutl = controller.check_connection()
        logger.info(f"Robot connection result: {type(resutl)}")
        # battery_level = resutl["battery_level"]
        # is_on_charger_platform = resutl["is_on_charger_platform"]
        # logger.info(f"battery_level: {battery_level} is_on_charger_platform: {is_on_charger_platform}")
        
        communication_interface.publish_robot_status("Awake")
        
        while communication_interface.start_command != "set_up":
            time.sleep(1)

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
