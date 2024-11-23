import queue
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
        self.start_command = False
        self.max_retries = 5
        self.delay = 10

        self.message_queue = queue.Queue()
        self.subscribe_to_topics()

    def subscribe_to_topics(self):
        self.subscribe("service/checkin", self.handle_start_command)

    def handle_start_command(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            message = payload.get("message", "")
            max_retries = payload.get("max_retries", 5)
            delay = payload.get("delay", 10)
            print(f"message = {message}")
        except json.JSONDecodeError:
            print("Invalid JSON payload. Using default retry parameters.")
            max_retries = 5
            delay = 10

        # Invoke the callback function if it exists
        if message == "start":
            # self.on_start_command(max_retries, delay)
            self.start_command = True
            self.max_retries = max_retries
            self.delay = delay
        
    def thread_safe_publish(self, topic, message):
        # print(f"Thread safe publish: {topic}, {message}")
        self.message_queue.put((topic, message))

    def process_message_queue(self):
        while not self.message_queue.empty():
            topic, message = self.message_queue.get()
            print(f"Processing message queue: topic = {topic}, message = {message}")
            self.publish(topic, message)

    def publish_status(self, status, message="", details=None):
        payload = {
            "status": status,
            "message": message,
            "details": details,
            # "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish("service_status/check_in", json.dumps(payload))

    def publish_message(self, sender, content, message_type="response"):
        message = {
            "sender": sender,
            "message_type": message_type,
            "content": content
        }
        json_message = json.dumps(message)
        self.thread_safe_publish("conv/hist", json_message)

    def publish_behaviour_complete(self):
        payload = {
            "status": "completed",
            "message": "",
            "details": "",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish("service/voice_assistant_status", json.dumps(payload))
