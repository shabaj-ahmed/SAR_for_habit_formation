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
        self.collect_response = False
        self.format = "open-ended"
        self.max_retries = 5
        self.delay = 10

        self.service_status = "Awake" # As soon as the voice assistant starts, it is awake

        self.message_queue = queue.Queue()

        # Subscription topics
        self.service_status_requested_topic = "request/service_status"
        self.control_cmd = "speech_recognition_control_cmd"
        self.record_response_topic = "speech_recognition/record_response"
        self.update_state_topic = "service/speech_recognition/update_state"

        # Publish topics
        self.speech_recognition_status_topic = "speech_recognition_status"
        self.vocie_assistant_hearbeat_topic = "speech_recognition_heartbeat"
        self.conversation_history_topic = "conversation/history"
        self.silance_detected_topic = "speech_recognition/silence_detected"
        self.audio_active_topic = "audio_active"
        self.check_in_controls_topic = "check_in_controller"
        self.robot_control_status_topic = "robot_control_status"

        # subscribe to topics
        self.subscribe(self.service_status_requested_topic, self._respond_with_service_status)
        self.subscribe(self.control_cmd, self._handle_command)
        self.subscribe(self.record_response_topic, self._handle_record_response)
        self.subscribe(self.update_state_topic, self._update_service_state)

    def _respond_with_service_status(self, client, userdata, message):
        self.publish_speech_recognition_status(self.service_status)
    
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

        status = {
            "set_up": "ready",
            "start": "running",
            "end": "completed"
        }

        self.publish_speech_recognition_status(status[cmd])

    def _handle_record_response(self, client, userdata, message):
        self.collect_response = True
        self.format = message.payload.decode("utf-8")

    def _update_service_state(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            state_name = payload.get("state_name", "")
            state = payload.get("state_value", [])
            self.logger.info(f"Received state update for {state_name}: {state}")
            # self.dispatcher.dispatch_event("update_service_state", payload)
            self.service_status = "set_up"
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload for updating service state. Using default retry parameters.")

    def publish_user_response(self, content, message_type="response"):
        self.logger.info(f"Publishing User response to conversation history topic: {content}")
        self.collect_response = False

        message = {
            "sender": "user",
            "message_type": message_type,
            "content": content
        }
        self._thread_safe_publish(self.conversation_history_topic, json.dumps(message))

        status = {
            "behaviour_name": "user response",
            "status": "failed" if content == "" else "complete",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        self._thread_safe_publish(self.robot_control_status_topic, json.dumps(status))
    
    def publish_speech_recognition_status(self, status, message="", details=None):
        if status == "running":
            self.publish(self.audio_active_topic, "1")
        if status == "completed":
            self.command = False
            self.publish(self.audio_active_topic, "0")
        
        payload = {
            "service_name": "speech_recognition",
            "status": status,
            "message": message,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish(self.speech_recognition_status_topic, json.dumps(payload))

        self.service_status = status

    def publish_speech_recognition_heartbeat(self):
        payload = {
            "service_name": "speech_recognition",
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
    
    def _thread_safe_publish(self, topic, message):
        self.logger.info(f"Thread safe publish: {topic}, {message}")
        self.message_queue.put((topic, message))
    
    def process_message_queue(self):
        while not self.message_queue.empty():
            topic, message = self.message_queue.get()
            self.publish(topic, message)
