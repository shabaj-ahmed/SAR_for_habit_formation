from shared_libraries.mqtt_client_base import MQTTClientBase
import json
import time

class CommunicationInterface(MQTTClientBase):
    def __init__(self, broker_address, port):
        super().__init__(broker_address, port)
        self.on_start_command = None  # Define a callback attribute
        self.subscribe_to_topics()

    def subscribe_to_topics(self):
        print("Subscribing to topics...")
        self.mqtt_client.subscribe("service/start")
        self.mqtt_client.message_callback_add("service/start", self.handle_start_command)

    def handle_start_command(self, client, userdata, message):
        print("Start command received.")
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            max_retries = payload.get("max_retries", 5)
            delay = payload.get("delay", 10)
        except json.JSONDecodeError:
            print("Invalid JSON payload. Using default retry parameters.")
            max_retries = 5
            delay = 10

        # Invoke the callback function if it exists
        if self.on_start_command:
            self.on_start_command(max_retries, delay)

    def publish_status(self, status, message, details=None):
        payload = {
            "status": status,
            "message": message,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.mqtt_client.publish("service/voice_assistant_status", json.dumps(payload))

    def publish_message(self, sender, content, message_type="response"):
        message = {
            "sender": sender,
            "type": message_type,
            "content": content
        }
        json_message = json.dumps(message)
        print(f"Publishing message: {json_message}")
        self.mqtt_client.publish("conversation/history", json_message)

    def publish_behaviour_complete(self):
        payload = {
            "status": "completed",
            "message": "",
            "details": "",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.mqtt_client.publish("service/voice_assistant_status", json.dumps(payload))
