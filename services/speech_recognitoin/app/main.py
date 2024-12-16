from src.communication_interface import CommunicationInterface
import time
import threading
import traceback
import os
import logging
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
sys.path.insert(0, project_root)
from shared_libraries.logging_config import setup_logger

def publish_heartbeat():
    while True:
        # Publish voice assistant heartbeat
        logger.info("voice assistant heartbeat")
        communication_interface.publish_speech_recognition_heartbeat()
        time.sleep(30)  # Publish heartbeat every 30 seconds

def process_communication_queue():
    while True:
        communication_interface.process_message_queue()
        time.sleep(0.5)

def setup_communication():
    interface = CommunicationInterface(
        broker_address=str(os.getenv("MQTT_BROKER_ADDRESS")),
        port=int(os.getenv("MQTT_BROKER_PORT"))
    )
    return interface

if __name__ == "__main__":
    setup_logger()

    logger = logging.getLogger("Main")
    
    communication_interface = setup_communication()

    threading.Thread(target=publish_heartbeat, daemon=True).start()
    threading.Thread(target=process_communication_queue, daemon=True).start()
    
    communication_interface.publish_speech_recognition_status("Awake")

    # Keep the program running to listen for commands
    try:
        while True:
            attempt = 0
            if communication_interface.command != "":
                while attempt < communication_interface.max_retries:
                    try:
                        while communication_interface.command != "":
                            pass
                        break  # Exit the loop if successful
                    except Exception as e:
                        attempt += 1
                        error_details = traceback.format_exc()
                        logger.error(f"Attempt {attempt}: {e}")
                        logger.error(error_details)
                        communication_interface.publish_speech_recognition_status("error", f"Attempt {attempt}: {e}", details=error_details)

                        if attempt < communication_interface.max_retries:
                            time.sleep(communication_interface.delay)
                        else:
                            logger.error("Max retries reached. Service stopped.")
                            communication_interface.publish_speech_recognition_status("failure", "Max retries reached. Service stopped.")
                            break
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Exiting voice assistant service...")
        communication_interface.disconnect()
