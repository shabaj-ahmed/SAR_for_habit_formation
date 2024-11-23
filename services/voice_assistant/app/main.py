from communication_interface import CommunicationInterface
from decision_tree import DecisionTree
import time
import threading
import traceback
from dotenv import load_dotenv
from pathlib import Path
import os
import json

# Relative path to the .env file in the config directory
# Move up one level and into config
dotenv_path = Path('../../configurations/.env')

# Load the .env file
load_dotenv(dotenv_path=dotenv_path)

decision_tree = DecisionTree()

def publish_heartbeat():
    while True:
        communication_interface.publish_status("running")
        time.sleep(30)  # Publish heartbeat every 30 seconds

def main_logic():
    decision_tree.check_in()
    communication_interface.publish_behaviour_complete()

# def on_start_command(max_retries, delay):
#     attempt = 0
#     while attempt < max_retries:
#         try:
#             communication_interface.thread_safe_publish("conv/hist", json.dumps({
#                 "sender": "Robot",
#                 "message_type": "question",
#                 "content": "This is a test question."
#             }))
#             main_logic()
#             communication_interface.publish_status("completed")
#             break  # Exit the loop if successful
#         except Exception as e:
#             attempt += 1
#             error_details = traceback.format_exc()
#             communication_interface.publish_status("error", f"Attempt {attempt}: {e}", details=error_details)

#             if attempt < max_retries:
#                 time.sleep(delay)
#             else:
#                 communication_interface.publish_status("failure", "Max retries reached. Service stopped.")
#                 break

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
    communication_interface = setup_communication()

    threading.Thread(target=publish_heartbeat, daemon=True).start()
    threading.Thread(target=process_communication_queue, daemon=True).start()

    decision_tree.communication_interface = communication_interface

    # Keep the program running to listen for commands
    try:
        while True:
            attempt = 0
            if communication_interface.start_command:
                while attempt < communication_interface.max_retries:
                    try:
                        main_logic()
                        communication_interface.publish_status("completed")
                        break  # Exit the loop if successful
                    except Exception as e:
                        attempt += 1
                        error_details = traceback.format_exc()
                        communication_interface.publish_status("error", f"Attempt {attempt}: {e}", details=error_details)

                        if attempt < communication_interface.max_retries:
                            time.sleep(communication_interface.delay)
                        else:
                            communication_interface.publish_status("failure", "Max retries reached. Service stopped.")
                            break
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down service...")
        communication_interface.disconnect()
