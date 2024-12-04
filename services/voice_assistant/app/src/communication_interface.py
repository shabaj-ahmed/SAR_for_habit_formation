import queue
import json
import time
import sys
import os
import logging

# Add the project root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
sys.path.insert(0, project_root)

from services.shared_libraries.mqtt_client_base import MQTTClientBase

class CommunicationInterface(MQTTClientBase):
    def __init__(self, broker_address, port):
        super().__init__(broker_address, port)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.start_command = False
        self.max_retries = 5
        self.delay = 10

        self.message_queue = queue.Queue()

        # Subscription topics
        self.check_in_status_topic = "check_in_status"

        # Publish topics
        self.audio_active_topic = "audio_active"
        self.conversation_history_topic = "conversation/history"
        self.robot_speech_topic = "voice_assistant/robot_speech"
        self.voice_assistant_status_topic = "voice_assistant_status"
        self.silance_detected_topic = "voice_assistant/silance_detected"

        # subscribe to topics
        self.subscribe(self.check_in_status_topic, self._handle_start_command)
    
    def _handle_start_command(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            message = payload.get("message", "")
            self.logger.info(f"message = {message}")
            if message == "start" or message == "running":
                self.start_command = True
                self.publish(self.audio_active_topic, "1")
            elif message == "completed" or message == "end":
                self.start_command = False
                self.publish(self.audio_active_topic, "0")
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload. Using default retry parameters.")
    
    def _handle_robot_speech(self, client, userdata, message):
        # Forwards the robot speech to the conversation history
        self._thread_safe_publish(self.conversation_history_topic, message.payload.decode("utf-8"))

    def publish_robot_speech(self, content, message_type="response"):
        message = {
            "sender": "robot",
            "message_type": message_type,
            "content": content
        }
        json_message = json.dumps(message)
        # This is what the robot should say
        self._thread_safe_publish(self.robot_speech_topic, json_message)

    def publish_user_response(self, content, message_type="response"):
        message = {
            "sender": "user",
            "message_type": message_type,
            "content": content
        }
        json_message = json.dumps(message)
        # This is what the user said
        self._thread_safe_publish(self.conversation_history_topic, json_message)
        
    
    def publish_voice_assistant_status(self, status, message="", details=None):
        if status == "completed":
            self.start_command = False
        payload = {
            "status": status,
            "message": message,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish(self.voice_assistant_status_topic, json.dumps(payload))
    
    def silance_detected(self):
        ''' Publish silence detected message to allow the UI to to show the user that the voice assistant will capture what they said '''
        self.publish(self.silance_detected_topic, "1")
    
    def _thread_safe_publish(self, topic, message):
        self.logger.info(f"Thread safe publish: {topic}, {message}")
        self.message_queue.put((topic, message))
    
    def process_message_queue(self):
        while not self.message_queue.empty():
            topic, message = self.message_queue.get()
            self.publish(topic, message)
