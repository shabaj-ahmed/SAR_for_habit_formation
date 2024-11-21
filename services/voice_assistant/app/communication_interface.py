import json
import time
import sys
import os

# Add the project root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, project_root)

from services.shared_libraries.mqtt_client_base import MQTTClientBase


class CommunicationInterface(MQTTClientBase):
    def __init__(self, broker_address, port):
        super().__init__(broker_address, port)
        self.on_start_command = None  # Define a callback attribute
        self.subscribe_to_topics()

    def subscribe_to_topics(self):
        self.subscribe("service/checkin", self.handle_start_command)

    def handle_start_command(self, client, userdata, message):
        print("Start command received.")
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            message = payload.get("message", "")
            max_retries = payload.get("max_retries", 5)
            delay = payload.get("delay", 10)
        except json.JSONDecodeError:
            print("Invalid JSON payload. Using default retry parameters.")
            max_retries = 5
            delay = 10

        # Invoke the callback function if it exists
        if self.on_start_command and message == "start":
            self.on_start_command(max_retries, delay)

    def publish_status(self, status, message="", details=None):
        payload = {
            "status": status,
            "message": message,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish("service_status/check_in", json.dumps(payload))

    def publish_message(self, sender, content, message_type="response"):
        message = {
            "sender": sender,
            "type": message_type,
            "content": content
        }
        json_message = json.dumps(message)
        print(f"Publishing message: {json_message}")
        self.publish("conversation/history", json_message)

    def publish_behaviour_complete(self):
        payload = {
            "status": "completed",
            "message": "",
            "details": "",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish("service/voice_assistant_status", json.dumps(payload))
