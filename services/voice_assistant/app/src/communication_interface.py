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

from shared_libraries.mqtt_client_base import MQTTClientBase

class CommunicationInterface(MQTTClientBase):
    def __init__(self, broker_address, port):
        super().__init__(broker_address, port)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.command = ""
        self.max_retries = 5
        self.delay = 10

        self.message_queue = queue.Queue()

        # Subscription topics
        self.control_cmd = "voice_assistant_control_cmd"

        # Publish topics
        self.voice_assistant_status_topic = "voice_assistant_status"
        self.vocie_assistant_hearbeat_topic = "voice_assistant_heartbeat"
        self.conversation_history_topic = "conversation/history"
        self.robot_speech_topic = "voice_assistant/robot_speech"
        self.silance_detected_topic = "voice_assistant/silence_detected"
        self.audio_active_topic = "audio_active"
        self.check_in_controls_topic = "check_in_controller"

        # subscribe to topics
        self.subscribe(self.control_cmd, self._handle_command)
    
    def _handle_command(self, client, userdata, message):
        
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            cmd = payload.get("cmd", "")
            logging.info(f"vocie assistant received the command: {cmd}")
            self.logger.info(f"cmd = {cmd}")
            if cmd == "end":
                self.command = ""
            elif cmd == "set_up" or cmd == "start":
                self.command = cmd
            else:
                self.command = ""
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
        if status == "running":
            self.publish(self.audio_active_topic, "1")
        if status == "completed":
            self.command = False
            self.publish(self.audio_active_topic, "0")
        
        payload = {
            "service_name": "voice_assistant",
            "status": status,
            "message": message,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish(self.voice_assistant_status_topic, json.dumps(payload))

    def publish_voice_assistant_heartbeat(self):
        payload = {
            "service_name": "voice_assistant",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish(self.vocie_assistant_hearbeat_topic, json.dumps(payload))
    
    def publish_silance_detected(self, duration):
        '''
        Publish silence detected message to allow the UI to to show the user that the voice assistant will capture what they said

        Args:
            duration (int): The duration of the silence
        '''
        logging.info(f"Silence detected. Duration: {duration}")
        self.publish(self.silance_detected_topic, duration)

    def end_check_in(self):
        logging.infor("Voice assistant ending check in process")
        self.publish(self.check_in_controls_topic, "0")
    
    def _thread_safe_publish(self, topic, message):
        self.logger.info(f"Thread safe publish: {topic}, {message}")
        self.message_queue.put((topic, message))
    
    def process_message_queue(self):
        while not self.message_queue.empty():
            topic, message = self.message_queue.get()
            self.publish(topic, message)
